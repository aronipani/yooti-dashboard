"""
Unit tests for POST /metrics/ingest Lambda handler.
All tests use @mock_aws — no real DynamoDB calls.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import json
from decimal import Decimal

import boto3
import pytest
from moto import mock_aws

from src.repository.metrics_repository import MetricsRepository

TABLE_NAME = "yooti-metrics"
PROJECT_ID = "yooti-ri"


@pytest.fixture(autouse=True)
def aws_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("TABLE_NAME", TABLE_NAME)


def _create_table(dynamodb: object) -> object:
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


def _valid_payload() -> dict:
    return {
        "project_id": PROJECT_ID,
        "sprint_num": 10,
        "stories": [
            {"story_id": "PROJ-1", "type": "feature", "status": "shipped"},
            {"story_id": "PROJ-2", "type": "bugfix", "status": "shipped"},
        ],
        "cycle_time_avg_days": 3.5,
        "stories_shipped": 2,
    }


def _make_event(body: dict | None = None) -> dict:
    return {
        "body": json.dumps(body) if body else None,
        "queryStringParameters": None,
        "pathParameters": None,
    }


def _patch_handler_repo(dynamodb: object) -> None:
    """Patch the handler module's repo with a fresh instance pointing at mock DynamoDB."""
    from src.handlers import ingest_metrics
    ingest_metrics.repo = MetricsRepository(dynamodb_resource=dynamodb)


class TestIngestValidPayload:
    """AC-1: valid payload → 201 with sprint_num."""

    @mock_aws
    def test_returns_201_on_first_ingest(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _patch_handler_repo(dynamodb)

        from src.handlers import ingest_metrics
        response = ingest_metrics.handler(_make_event(_valid_payload()), None)

        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["sprint_num"] == 10
        assert body["stories_ingested"] == 2

    @mock_aws
    def test_writes_sprint_summary_to_dynamodb(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _patch_handler_repo(dynamodb)

        from src.handlers import ingest_metrics
        ingest_metrics.handler(_make_event(_valid_payload()), None)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        summary = repo.get_sprint_summary(PROJECT_ID, 10)
        assert summary is not None

    @mock_aws
    def test_writes_stories_to_dynamodb(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _patch_handler_repo(dynamodb)

        from src.handlers import ingest_metrics
        ingest_metrics.handler(_make_event(_valid_payload()), None)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        stories = repo.get_sprint_stories(PROJECT_ID, 10)
        assert len(stories) == 2


class TestIngestIdempotent:
    """AC-2: same sprint payload twice → 200 not 409."""

    @mock_aws
    def test_returns_200_on_re_ingest(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _patch_handler_repo(dynamodb)

        from src.handlers import ingest_metrics
        payload = _valid_payload()
        first = ingest_metrics.handler(_make_event(payload), None)
        second = ingest_metrics.handler(_make_event(payload), None)

        assert first["statusCode"] == 201
        assert second["statusCode"] == 200


class TestIngestMissingProjectId:
    """AC-3: missing project_id → 400 INVALID_PROJECT_ID."""

    @mock_aws
    def test_returns_400_when_project_id_missing(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _patch_handler_repo(dynamodb)

        from src.handlers import ingest_metrics
        payload = {"sprint_num": 10, "stories": []}
        response = ingest_metrics.handler(_make_event(payload), None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["error"] == "INVALID_PROJECT_ID"

    @mock_aws
    def test_returns_400_when_project_id_empty(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _patch_handler_repo(dynamodb)

        from src.handlers import ingest_metrics
        payload = {"project_id": "", "sprint_num": 10, "stories": []}
        response = ingest_metrics.handler(_make_event(payload), None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["error"] == "INVALID_PROJECT_ID"


class TestIngestInvalidBody:
    @mock_aws
    def test_returns_400_on_invalid_json(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _patch_handler_repo(dynamodb)

        from src.handlers import ingest_metrics
        event = {"body": "not json{{{", "queryStringParameters": None}
        response = ingest_metrics.handler(event, None)

        assert response["statusCode"] == 400

    @mock_aws
    def test_returns_400_when_sprint_num_missing(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _patch_handler_repo(dynamodb)

        from src.handlers import ingest_metrics
        payload = {"project_id": PROJECT_ID, "stories": []}
        response = ingest_metrics.handler(_make_event(payload), None)

        assert response["statusCode"] == 400

    @mock_aws
    def test_returns_400_when_stories_not_array(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _patch_handler_repo(dynamodb)

        from src.handlers import ingest_metrics
        payload = {"project_id": PROJECT_ID, "sprint_num": 10, "stories": "not-array"}
        response = ingest_metrics.handler(_make_event(payload), None)

        assert response["statusCode"] == 400


class TestIngestSnapshotUpdate:
    """AC-5: CURRENT#SNAPSHOT updated with KPIs and insight alerts."""

    @mock_aws
    def test_updates_current_snapshot_after_ingest(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _patch_handler_repo(dynamodb)

        from src.handlers import ingest_metrics
        payload = _valid_payload()
        ingest_metrics.handler(_make_event(payload), None)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        snapshot = repo.get_current_snapshot(PROJECT_ID)
        assert snapshot is not None
        assert snapshot["sprint_num"] == 10
        assert "last_ingested_at" in snapshot
        assert "insight_alerts" in snapshot

    @mock_aws
    def test_computes_insight_alerts_in_snapshot(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _patch_handler_repo(dynamodb)

        from src.handlers import ingest_metrics
        payload = _valid_payload()
        payload["regression_rate_pct"] = 12.0  # Should trigger REGRESSION_SPIKE
        ingest_metrics.handler(_make_event(payload), None)

        repo = MetricsRepository(dynamodb_resource=dynamodb)
        snapshot = repo.get_current_snapshot(PROJECT_ID)
        assert snapshot is not None
        alerts = snapshot.get("insight_alerts", [])
        alert_types = [a["type"] for a in alerts]
        assert "REGRESSION_SPIKE" in alert_types


class TestIngestDynamoUnavailable:
    """AC-4: DynamoDB unavailable → 500 INTERNAL_ERROR."""

    @mock_aws
    def test_returns_500_on_repository_error(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        # Do NOT create table — forces ClientError
        _patch_handler_repo(dynamodb)

        from src.handlers import ingest_metrics
        response = ingest_metrics.handler(_make_event(_valid_payload()), None)

        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert body["error"] == "INTERNAL_ERROR"
        # Verify no internal detail exposed
        assert "ClientError" not in body.get("message", "")
        assert "Traceback" not in body.get("message", "")
