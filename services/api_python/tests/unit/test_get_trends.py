"""
Unit tests for get_trends Lambda handler.
All tests use @mock_aws — no real DynamoDB calls.
Covers AC-1 (filtered metric with deltas), AC-2 (all metrics grouped).
"""
import json
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import boto3
import pytest
from moto import mock_aws

from src.repository.metrics_repository import MetricsRepository

PROJECT_ID = "yooti-ri"
TABLE_NAME = "yooti-metrics"


@pytest.fixture(autouse=True)
def aws_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set required env vars for every test."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("TABLE_NAME", TABLE_NAME)


@pytest.fixture(autouse=True)
def _reset_module_repo() -> None:
    """Reset the module-level repo so each test gets a fresh instance under mock_aws."""
    import src.repository.metrics_repository as repo_mod
    import src.handlers.get_trends as handler_mod

    repo_mod._dynamodb_resource = None
    handler_mod.repo = MetricsRepository()
    handler_mod.repo._table_ref = None


def _create_table(dynamodb: object) -> object:
    """Create the yooti-metrics table matching ARCH-DASHBOARD.md."""
    return dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )


def _seed_trend_points(repo: MetricsRepository) -> None:
    """Seed 5 cycle_time_avg trend points and 3 sprint_completion_pct points."""
    cycle_values = [
        (1, Decimal("4.0")),
        (2, Decimal("3.8")),
        (3, Decimal("3.5")),
        (4, Decimal("3.5")),
        (5, Decimal("3.2")),
    ]
    for sprint_num, value in cycle_values:
        repo.put_trend_point(PROJECT_ID, "cycle_time_avg", sprint_num, value)

    completion_values = [
        (1, Decimal("80.0")),
        (2, Decimal("85.0")),
        (3, Decimal("82.0")),
    ]
    for sprint_num, value in completion_values:
        repo.put_trend_point(
            PROJECT_ID, "sprint_completion_pct", sprint_num, value,
        )


def _make_event(
    project_id: str | None = None,
    metric: str | None = None,
) -> dict:
    """Build a mock API Gateway event."""
    params: dict[str, str] | None = None
    if project_id is not None or metric is not None:
        params = {}
        if project_id is not None:
            params["project_id"] = project_id
        if metric is not None:
            params["metric"] = metric
    return {"queryStringParameters": params}


class TestGetTrendsAC1:
    """AC-1: 5 trend points for cycle_time_avg with delta and direction."""

    @mock_aws
    def test_returns_5_cycle_time_points(self) -> None:
        """Filter by metric=cycle_time_avg returns 5 enriched points."""
        from src.handlers.get_trends import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_trend_points(repo)

        result = handler(_make_event(PROJECT_ID, "cycle_time_avg"), None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        points = body["trends"]["cycle_time_avg"]
        assert len(points) == 5

    @mock_aws
    def test_first_point_has_zero_delta(self) -> None:
        """First point delta_from_prev is 0 and direction is flat."""
        from src.handlers.get_trends import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_trend_points(repo)

        result = handler(_make_event(PROJECT_ID, "cycle_time_avg"), None)
        body = json.loads(result["body"])
        first = body["trends"]["cycle_time_avg"][0]

        assert first["delta_from_prev"] == 0.0
        assert first["direction"] == "flat"

    @mock_aws
    def test_subsequent_points_have_delta_and_direction(self) -> None:
        """Points after the first have correct delta and direction."""
        from src.handlers.get_trends import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_trend_points(repo)

        result = handler(_make_event(PROJECT_ID, "cycle_time_avg"), None)
        body = json.loads(result["body"])
        points = body["trends"]["cycle_time_avg"]

        # Sprint 2: 3.8 - 4.0 = -0.2 -> down
        assert points[1]["direction"] == "down"
        assert points[1]["delta_from_prev"] == pytest.approx(-0.2)

        # Sprint 4: 3.5 - 3.5 = 0 -> flat
        assert points[3]["direction"] == "flat"
        assert points[3]["delta_from_prev"] == 0.0

    @mock_aws
    def test_points_sorted_ascending_by_sprint(self) -> None:
        """Points are returned sorted by sprint_num ascending."""
        from src.handlers.get_trends import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_trend_points(repo)

        result = handler(_make_event(PROJECT_ID, "cycle_time_avg"), None)
        body = json.loads(result["body"])
        sprint_nums = [p["sprint_num"] for p in body["trends"]["cycle_time_avg"]]

        assert sprint_nums == [1, 2, 3, 4, 5]

    @mock_aws
    def test_each_point_has_required_fields(self) -> None:
        """Each point has sprint_num, value, delta_from_prev, direction."""
        from src.handlers.get_trends import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_trend_points(repo)

        result = handler(_make_event(PROJECT_ID, "cycle_time_avg"), None)
        body = json.loads(result["body"])

        for point in body["trends"]["cycle_time_avg"]:
            assert "sprint_num" in point
            assert "value" in point
            assert "delta_from_prev" in point
            assert "direction" in point


class TestGetTrendsAC2:
    """AC-2: no metric filter returns all metric series grouped by metric_name."""

    @mock_aws
    def test_returns_all_metrics_grouped(self) -> None:
        """No metric param returns both cycle_time_avg and sprint_completion_pct."""
        from src.handlers.get_trends import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_trend_points(repo)

        result = handler(_make_event(PROJECT_ID), None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "cycle_time_avg" in body["trends"]
        assert "sprint_completion_pct" in body["trends"]
        assert len(body["trends"]["cycle_time_avg"]) == 5
        assert len(body["trends"]["sprint_completion_pct"]) == 3

    @mock_aws
    def test_each_group_is_enriched(self) -> None:
        """Each metric group has delta_from_prev and direction on every point."""
        from src.handlers.get_trends import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_trend_points(repo)

        result = handler(_make_event(PROJECT_ID), None)
        body = json.loads(result["body"])

        for _name, points in body["trends"].items():
            for point in points:
                assert "delta_from_prev" in point
                assert "direction" in point


class TestGetTrendsValidation:
    """Validation: missing or empty project_id returns 400."""

    @mock_aws
    def test_returns_400_when_project_id_missing(self) -> None:
        """No project_id param — handler returns 400."""
        from src.handlers.get_trends import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        result = handler(_make_event(None), None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"] == "INVALID_PROJECT_ID"

    @mock_aws
    def test_returns_400_when_project_id_empty(self) -> None:
        """Empty project_id — handler returns 400."""
        from src.handlers.get_trends import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        result = handler(_make_event(""), None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"] == "INVALID_PROJECT_ID"

    @mock_aws
    def test_response_excludes_pk_sk(self) -> None:
        """DynamoDB keys PK and SK must not appear in response."""
        from src.handlers.get_trends import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_trend_points(repo)

        result = handler(_make_event(PROJECT_ID, "cycle_time_avg"), None)
        body = json.loads(result["body"])

        for point in body["trends"]["cycle_time_avg"]:
            assert "PK" not in point
            assert "SK" not in point

    @mock_aws
    def test_response_has_cors_headers(self) -> None:
        """Response must include CORS headers."""
        from src.handlers.get_trends import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_trend_points(repo)

        result = handler(_make_event(PROJECT_ID), None)

        assert result["headers"]["Access-Control-Allow-Origin"] == "*"

    @mock_aws
    def test_empty_trends_when_no_data(self) -> None:
        """No trend data seeded returns empty trends dict."""
        from src.handlers.get_trends import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        result = handler(_make_event(PROJECT_ID), None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["trends"] == {}
