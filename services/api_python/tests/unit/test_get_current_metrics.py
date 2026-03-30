"""
Unit tests for get_current_metrics Lambda handler.
All tests use @mock_aws — no real DynamoDB calls.
Covers AC-1 (200 with snapshot), AC-2 (404), AC-3 (400).
"""
import json
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import boto3
import pytest
from moto import mock_aws

from src.repository.keys import pk, sk_current_snapshot
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
    import src.handlers.get_current_metrics as handler_mod

    repo_mod._dynamodb_resource = None
    handler_mod.repo = MetricsRepository()
    handler_mod.repo._table_ref = None


def _create_table(dynamodb: object) -> object:
    """Create the yooti-metrics table matching ARCH-DASHBOARD.md."""
    table = dynamodb.create_table(
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
    return table


def _seed_current_snapshot(table: object) -> dict:
    """Seed a current snapshot record."""
    item = {
        "PK": pk(PROJECT_ID),
        "SK": sk_current_snapshot(),
        "project_id": PROJECT_ID,
        "sprint_num": 3,
        "kpis": {
            "cycle_time_avg_days": Decimal("3.5"),
            "sprint_completion_pct": Decimal("85.0"),
            "stories_shipped": 5,
        },
        "insights": ["Velocity is trending up", "One blocker resolved late"],
        "last_ingested_at": "2026-03-28T12:00:00Z",
    }
    table.put_item(Item=item)
    return item


def _make_event(project_id: str | None = None) -> dict:
    """Build a mock API Gateway event."""
    if project_id is not None:
        return {"queryStringParameters": {"project_id": project_id}}
    return {"queryStringParameters": None}


class TestGetCurrentMetricsAC1:
    """AC-1: snapshot exists -> 200 with kpis, insights, sprint_num, last_ingested_at."""

    @mock_aws
    def test_returns_200_with_snapshot(self) -> None:
        """Happy path — snapshot exists, handler returns 200."""
        from src.handlers.get_current_metrics import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        _seed_current_snapshot(table)

        result = handler(_make_event(PROJECT_ID), None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["sprint_num"] == 3
        assert "kpis" in body
        assert "insights" in body
        assert body["last_ingested_at"] == "2026-03-28T12:00:00Z"

    @mock_aws
    def test_response_excludes_pk_sk(self) -> None:
        """Internal DynamoDB keys PK and SK must not appear in response."""
        from src.handlers.get_current_metrics import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        _seed_current_snapshot(table)

        result = handler(_make_event(PROJECT_ID), None)

        body = json.loads(result["body"])
        assert "PK" not in body
        assert "SK" not in body

    @mock_aws
    def test_response_has_cors_headers(self) -> None:
        """Response must include CORS headers."""
        from src.handlers.get_current_metrics import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        _seed_current_snapshot(table)

        result = handler(_make_event(PROJECT_ID), None)

        assert result["headers"]["Access-Control-Allow-Origin"] == "*"
        assert "Content-Type" in result["headers"]


class TestGetCurrentMetricsAC2:
    """AC-2: no snapshot -> 404 SPRINT_NOT_FOUND."""

    @mock_aws
    def test_returns_404_when_no_snapshot(self) -> None:
        """No snapshot seeded — handler returns 404."""
        from src.handlers.get_current_metrics import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        result = handler(_make_event(PROJECT_ID), None)

        assert result["statusCode"] == 404
        body = json.loads(result["body"])
        assert body["error"] == "SPRINT_NOT_FOUND"

    @mock_aws
    def test_returns_404_for_wrong_project(self) -> None:
        """Snapshot exists for different project — handler returns 404."""
        from src.handlers.get_current_metrics import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        _seed_current_snapshot(table)

        result = handler(_make_event("nonexistent-project"), None)

        assert result["statusCode"] == 404
        body = json.loads(result["body"])
        assert body["error"] == "SPRINT_NOT_FOUND"


class TestGetCurrentMetricsAC3:
    """AC-3: missing project_id -> 400 INVALID_PROJECT_ID."""

    @mock_aws
    def test_returns_400_when_project_id_missing(self) -> None:
        """No project_id param — handler returns 400."""
        from src.handlers.get_current_metrics import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        result = handler(_make_event(None), None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"] == "INVALID_PROJECT_ID"

    @mock_aws
    def test_returns_400_when_project_id_empty(self) -> None:
        """Empty string project_id — handler returns 400."""
        from src.handlers.get_current_metrics import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        result = handler(_make_event(""), None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"] == "INVALID_PROJECT_ID"

    @mock_aws
    def test_returns_400_when_project_id_whitespace(self) -> None:
        """Whitespace-only project_id — handler returns 400."""
        from src.handlers.get_current_metrics import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        result = handler(_make_event("   "), None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"] == "INVALID_PROJECT_ID"

    @mock_aws
    def test_returns_400_when_query_params_null(self) -> None:
        """queryStringParameters is null (API Gateway sends this)."""
        from src.handlers.get_current_metrics import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        event: dict = {"queryStringParameters": None}
        result = handler(event, None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"] == "INVALID_PROJECT_ID"
