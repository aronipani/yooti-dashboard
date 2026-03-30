"""
Unit tests for MetricsRepository write methods.
All tests use @mock_aws — no real DynamoDB calls.
AC-1: idempotent writes — same sprint_num twice, no error.
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
    """Create the yooti-metrics table."""
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


class TestPutSprintSummary:
    @mock_aws
    def test_writes_sprint_summary(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        data = {
            "cycle_time_avg_days": Decimal("3.5"),
            "sprint_completion_pct": Decimal("85.0"),
            "stories_shipped": 5,
        }
        repo.put_sprint_summary(PROJECT_ID, 10, data)

        response = table.get_item(
            Key={"PK": pk(PROJECT_ID), "SK": sk_sprint_summary(10)}
        )
        assert "Item" in response
        assert response["Item"]["sprint_num"] == 10

    @mock_aws
    def test_idempotent_write_succeeds_without_error(self) -> None:
        """AC-1: same sprint written twice — no error, no duplicate."""
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        data = {"cycle_time_avg_days": Decimal("3.5"), "stories_shipped": 5}
        repo.put_sprint_summary(PROJECT_ID, 10, data)

        # Second write with updated data — should succeed
        data["stories_shipped"] = 6
        repo.put_sprint_summary(PROJECT_ID, 10, data)

        result = repo.get_sprint_summary(PROJECT_ID, 10)
        assert result is not None
        assert result["stories_shipped"] == 6


class TestPutStoryMetrics:
    @mock_aws
    def test_writes_story_metrics(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        data = {
            "type": "feature",
            "status": "shipped",
            "cycle_time_hrs": Decimal("24.5"),
        }
        repo.put_story_metrics(PROJECT_ID, 10, "PROJ-123", data)

        response = table.get_item(
            Key={"PK": pk(PROJECT_ID), "SK": sk_story(10, "PROJ-123")}
        )
        assert "Item" in response
        assert response["Item"]["story_id"] == "PROJ-123"


class TestPutPhaseDurations:
    @mock_aws
    def test_writes_phase_durations(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        data = {"g1_wait": Decimal("2.0"), "phase2": Decimal("1.5")}
        repo.put_phase_durations(PROJECT_ID, 10, "PROJ-123", data)

        response = table.get_item(
            Key={"PK": pk(PROJECT_ID), "SK": sk_phase(10, "PROJ-123")}
        )
        assert "Item" in response


class TestPutTrendPoint:
    @mock_aws
    def test_writes_trend_point(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        repo.put_trend_point(PROJECT_ID, "cycle_time_avg", 10, Decimal("3.5"))

        response = table.get_item(
            Key={"PK": pk(PROJECT_ID), "SK": sk_trend("cycle_time_avg", 10)}
        )
        assert "Item" in response
        assert response["Item"]["value"] == Decimal("3.5")


class TestPutCurrentSnapshot:
    @mock_aws
    def test_writes_snapshot(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        data = {
            "sprint_num": 10,
            "last_ingested_at": "2026-03-01T00:00:00Z",
            "insight_alerts": [],
        }
        repo.put_current_snapshot(PROJECT_ID, data)

        result = repo.get_current_snapshot(PROJECT_ID)
        assert result is not None
        assert result["sprint_num"] == 10

    @mock_aws
    def test_overwrites_snapshot_on_update(self) -> None:
        """CURRENT#SNAPSHOT always overwrites — per architect annotation."""
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        repo.put_current_snapshot(PROJECT_ID, {"sprint_num": 10, "insight_alerts": []})
        repo.put_current_snapshot(PROJECT_ID, {"sprint_num": 11, "insight_alerts": []})

        result = repo.get_current_snapshot(PROJECT_ID)
        assert result is not None
        assert result["sprint_num"] == 11


class TestPutGateEvent:
    @mock_aws
    def test_writes_gate_event(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        data = {"timestamp": "2026-03-01T00:00:00Z", "reviewer": "dev1"}
        repo.put_gate_event(PROJECT_ID, "PROJ-123", 3, data)

        response = table.get_item(
            Key={"PK": pk(PROJECT_ID), "SK": sk_gate("PROJ-123", 3)}
        )
        assert "Item" in response


class TestPutEscalation:
    @mock_aws
    def test_writes_escalation(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = _create_table(dynamodb)
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        data = {"type": "SCOPE_ERROR", "sprint_num": 10}
        repo.put_escalation(PROJECT_ID, "PROJ-123", "T001", data)

        response = table.get_item(
            Key={"PK": pk(PROJECT_ID), "SK": sk_escalation("PROJ-123", "T001")}
        )
        assert "Item" in response


class TestBatchWriteSprint:
    @mock_aws
    def test_writes_all_sprint_entities(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        payload = {
            "summary": {
                "cycle_time_avg_days": Decimal("3.5"),
                "stories_shipped": 5,
            },
            "stories": [
                {
                    "story_id": "PROJ-1",
                    "type": "feature",
                    "status": "shipped",
                    "cycle_time_hrs": Decimal("24.0"),
                },
                {
                    "story_id": "PROJ-2",
                    "type": "bugfix",
                    "status": "shipped",
                    "cycle_time_hrs": Decimal("12.0"),
                },
            ],
            "trends": [
                {"metric_name": "cycle_time_avg", "value": Decimal("3.5")},
            ],
        }
        repo.batch_write_sprint(PROJECT_ID, 10, payload)

        # Verify summary written
        summary = repo.get_sprint_summary(PROJECT_ID, 10)
        assert summary is not None

        # Verify stories written
        stories = repo.get_sprint_stories(PROJECT_ID, 10)
        assert len(stories) == 2

        # Verify trends written
        trends = repo.get_trends(PROJECT_ID, metric="cycle_time_avg")
        assert len(trends) == 1

    @mock_aws
    def test_idempotent_batch_write(self) -> None:
        """AC-1: batch write same sprint twice — no error."""
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        payload = {
            "summary": {"stories_shipped": 5},
            "stories": [{"story_id": "PROJ-1", "type": "feature", "status": "shipped"}],
            "trends": [],
        }
        repo.batch_write_sprint(PROJECT_ID, 10, payload)
        repo.batch_write_sprint(PROJECT_ID, 10, payload)  # No error

        stories = repo.get_sprint_stories(PROJECT_ID, 10)
        assert len(stories) == 1


class TestWriteClientErrorHandling:
    @mock_aws
    def test_put_sprint_summary_raises_repository_error(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        with pytest.raises(RepositoryError):
            repo.put_sprint_summary(PROJECT_ID, 10, {"stories_shipped": 5})

    @mock_aws
    def test_put_current_snapshot_raises_repository_error(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        repo = MetricsRepository(dynamodb_resource=dynamodb)

        with pytest.raises(RepositoryError):
            repo.put_current_snapshot(PROJECT_ID, {"sprint_num": 10})
