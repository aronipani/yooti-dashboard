"""
Unit tests for MetricsRepository read methods.
All tests use @mock_aws — no real DynamoDB calls.
Each test verifies the correct access pattern (GetItem or Query, never Scan).
"""
import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import boto3
import pytest
from moto import mock_aws

from src.repository.errors import RepositoryError
from src.repository.keys import (
    pk,
    sk_sprint_summary,
    sk_story,
    sk_phase,
    sk_trend,
    sk_current_snapshot,
    sk_gate,
    sk_escalation,
)
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


def _seed_sprint_summary(table: object, sprint_num: int) -> dict:
    """Seed a sprint summary record."""
    item = {
        "PK": pk(PROJECT_ID),
        "SK": sk_sprint_summary(sprint_num),
        "sprint_num": sprint_num,
        "project_id": PROJECT_ID,
        "cycle_time_avg_days": Decimal("3.5"),
        "sprint_completion_pct": Decimal("85.0"),
        "stories_shipped": 5,
        "stories_committed": 6,
        "created_at": "2026-03-01T00:00:00Z",
        "updated_at": "2026-03-01T00:00:00Z",
    }
    table.put_item(Item=item)
    return item


def _seed_story(table: object, sprint_num: int, story_id: str) -> dict:
    """Seed a story metrics record."""
    item = {
        "PK": pk(PROJECT_ID),
        "SK": sk_story(sprint_num, story_id),
        "story_id": story_id,
        "sprint_num": sprint_num,
        "type": "feature",
        "status": "shipped",
        "cycle_time_hrs": Decimal("24.5"),
        "iteration_count": 2,
        "created_at": "2026-03-01T00:00:00Z",
        "updated_at": "2026-03-01T00:00:00Z",
    }
    table.put_item(Item=item)
    return item


def _seed_current_snapshot(table: object, sprint_num: int) -> dict:
    """Seed a current snapshot record."""
    item = {
        "PK": pk(PROJECT_ID),
        "SK": sk_current_snapshot(),
        "sprint_num": sprint_num,
        "project_id": PROJECT_ID,
        "cycle_time_avg_days": Decimal("3.5"),
        "sprint_completion_pct": Decimal("85.0"),
        "last_ingested_at": "2026-03-01T00:00:00Z",
        "insight_alerts": [],
    }
    table.put_item(Item=item)
    return item


def _seed_trend(table: object, metric: str, sprint_num: int, value: Decimal) -> dict:
    """Seed a trend point."""
    item = {
        "PK": pk(PROJECT_ID),
        "SK": sk_trend(metric, sprint_num),
        "metric_name": metric,
        "sprint_num": sprint_num,
        "value": value,
    }
    table.put_item(Item=item)
    return item


def _seed_phase(table: object, sprint_num: int, story_id: str) -> dict:
    """Seed phase durations for a story."""
    item = {
        "PK": pk(PROJECT_ID),
        "SK": sk_phase(sprint_num, story_id),
        "story_id": story_id,
        "sprint_num": sprint_num,
        "g1_wait": Decimal("2.0"),
        "phase2": Decimal("1.5"),
        "g2_wait": Decimal("4.0"),
        "phase4": Decimal("8.0"),
        "g3_wait": Decimal("3.0"),
        "g4_g5": Decimal("1.0"),
    }
    table.put_item(Item=item)
    return item


def _seed_gate(table: object, story_id: str, gate_num: int) -> dict:
    """Seed a gate event."""
    item = {
        "PK": pk(PROJECT_ID),
        "SK": sk_gate(story_id, gate_num),
        "story_id": story_id,
        "gate": f"G{gate_num}",
        "timestamp": "2026-03-01T00:00:00Z",
        "reviewer": "dev1",
    }
    table.put_item(Item=item)
    return item


def _seed_escalation(table: object, story_id: str, task_id: str) -> dict:
    """Seed an escalation record."""
    item = {
        "PK": pk(PROJECT_ID),
        "SK": sk_escalation(story_id, task_id),
        "story_id": story_id,
        "task_id": task_id,
        "type": "SCOPE_ERROR",
        "sprint_num": 10,
    }
    table.put_item(Item=item)
    return item


class TestGetCurrentSnapshot:
    """AC-4: get_current_snapshot uses single GetItem — not Query, not Scan."""

    @mock_aws
    def test_returns_snapshot_when_exists(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        _seed_current_snapshot(table, sprint_num=10)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_current_snapshot(PROJECT_ID)

        assert result is not None
        assert result["sprint_num"] == 10
        assert result["project_id"] == PROJECT_ID

    @mock_aws
    def test_returns_none_when_not_exists(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_current_snapshot(PROJECT_ID)

        assert result is None


class TestGetSprintSummary:
    """AC-2: get_sprint_summary uses single Query — no Scan."""

    @mock_aws
    def test_returns_summary_when_exists(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        _seed_sprint_summary(table, sprint_num=10)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_sprint_summary(PROJECT_ID, 10)

        assert result is not None
        assert result["sprint_num"] == 10
        assert result["cycle_time_avg_days"] == Decimal("3.5")

    @mock_aws
    def test_returns_none_when_not_exists(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_sprint_summary(PROJECT_ID, 99)

        assert result is None


class TestGetSprintStories:
    """AC-3: get_sprint_stories uses SK begins_with — one Query call."""

    @mock_aws
    def test_returns_all_stories_in_sprint(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        for i in range(5):
            _seed_story(table, sprint_num=10, story_id=f"PROJ-{i}")

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_sprint_stories(PROJECT_ID, 10)

        assert len(result) == 5

    @mock_aws
    def test_returns_empty_list_when_no_stories(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_sprint_stories(PROJECT_ID, 10)

        assert result == []

    @mock_aws
    def test_does_not_return_stories_from_other_sprints(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        _seed_story(table, sprint_num=10, story_id="PROJ-1")
        _seed_story(table, sprint_num=11, story_id="PROJ-2")

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_sprint_stories(PROJECT_ID, 10)

        assert len(result) == 1
        assert result[0]["story_id"] == "PROJ-1"


class TestGetSprintList:
    """All sprint summaries sorted descending by sprint_num."""

    @mock_aws
    def test_returns_all_summaries_sorted_descending(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        for num in [8, 10, 9, 7, 6]:
            _seed_sprint_summary(table, sprint_num=num)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_sprint_list(PROJECT_ID)

        assert len(result) == 5
        nums = [r["sprint_num"] for r in result]
        assert nums == [10, 9, 8, 7, 6]

    @mock_aws
    def test_returns_empty_when_no_sprints(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_sprint_list(PROJECT_ID)

        assert result == []


class TestGetTrends:
    """Trend series queried with begins_with on SK."""

    @mock_aws
    def test_returns_trends_for_specific_metric(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        for num in range(1, 6):
            _seed_trend(table, "cycle_time_avg", num, Decimal(str(num * 1.5)))

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_trends(PROJECT_ID, metric="cycle_time_avg")

        assert len(result) == 5

    @mock_aws
    def test_returns_all_trends_when_no_metric_filter(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        _seed_trend(table, "cycle_time_avg", 1, Decimal("3.5"))
        _seed_trend(table, "regression_rate", 1, Decimal("5.0"))

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_trends(PROJECT_ID)

        assert len(result) == 2

    @mock_aws
    def test_returns_empty_when_no_trends(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_trends(PROJECT_ID, metric="cycle_time_avg")

        assert result == []


class TestGetStoryDetail:
    """Story detail fetched with GetItem."""

    @mock_aws
    def test_returns_story_when_exists(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        _seed_story(table, sprint_num=10, story_id="PROJ-123")

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_story_detail(PROJECT_ID, 10, "PROJ-123")

        assert result is not None
        assert result["story_id"] == "PROJ-123"

    @mock_aws
    def test_returns_none_when_story_not_found(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_story_detail(PROJECT_ID, 10, "PROJ-999")

        assert result is None


class TestGetPhaseDurations:
    """Phase durations fetched with GetItem — AP-7."""

    @mock_aws
    def test_returns_phases_when_exist(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        _seed_phase(table, sprint_num=10, story_id="PROJ-123")

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_phase_durations(PROJECT_ID, 10, "PROJ-123")

        assert result is not None
        assert result["g1_wait"] == Decimal("2.0")

    @mock_aws
    def test_returns_none_when_no_phases(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_phase_durations(PROJECT_ID, 10, "PROJ-123")

        assert result is None


class TestGetGateEvents:
    """Gate events queried with begins_with — AP-8."""

    @mock_aws
    def test_returns_all_gates_for_story(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        for g in range(1, 4):
            _seed_gate(table, "PROJ-123", g)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_gate_events(PROJECT_ID, "PROJ-123")

        assert len(result) == 3

    @mock_aws
    def test_returns_empty_when_no_gates(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_gate_events(PROJECT_ID, "PROJ-123")

        assert result == []


class TestGetEscalations:
    """Escalation log queried with begins_with — AP-9."""

    @mock_aws
    def test_returns_escalations_for_story(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        _seed_escalation(table, "PROJ-123", "T001")
        _seed_escalation(table, "PROJ-123", "T002")

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_escalations(PROJECT_ID, "PROJ-123")

        assert len(result) == 2

    @mock_aws
    def test_returns_empty_when_no_escalations(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        result = repo.get_escalations(PROJECT_ID, "PROJ-123")

        assert result == []


class TestClientErrorHandling:
    """AC-5: ClientError caught and re-raised as RepositoryError."""

    @mock_aws
    def test_get_current_snapshot_raises_repository_error_on_client_error(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        # Do NOT create table — this will cause a ClientError
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        with pytest.raises(RepositoryError):
            repo.get_current_snapshot(PROJECT_ID)

    @mock_aws
    def test_get_sprint_summary_raises_repository_error_on_client_error(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        with pytest.raises(RepositoryError):
            repo.get_sprint_summary(PROJECT_ID, 10)

    @mock_aws
    def test_get_sprint_stories_raises_repository_error_on_client_error(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        with pytest.raises(RepositoryError):
            repo.get_sprint_stories(PROJECT_ID, 10)
