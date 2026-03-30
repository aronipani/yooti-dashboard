"""
Unit tests for get_story_detail Lambda handler.
All tests use @mock_aws — no real DynamoDB calls.
Covers AC-3 (story found with evidence), AC-4 (story not found 404).
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
    import src.handlers.get_story_detail as handler_mod

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


def _seed_story(repo: MetricsRepository) -> None:
    """Seed story PROJ-123 in sprint 3 with phases, gates, and escalations."""
    repo.put_story_metrics(
        PROJECT_ID, 3, "PROJ-123",
        {
            "cycle_time_days": Decimal("3.5"),
            "status": "COMPLETE",
            "complexity": "M",
        },
    )
    repo.put_phase_durations(
        PROJECT_ID, 3, "PROJ-123",
        {
            "phase_1_hours": Decimal("2.0"),
            "phase_2_hours": Decimal("5.0"),
            "phase_3_hours": Decimal("1.5"),
        },
    )
    repo.put_gate_event(
        PROJECT_ID, "PROJ-123", 1,
        {"signed_by": "dev@example.com", "signed_at": "2026-03-20T10:00:00Z"},
    )
    repo.put_gate_event(
        PROJECT_ID, "PROJ-123", 2,
        {"signed_by": "arch@example.com", "signed_at": "2026-03-21T14:00:00Z"},
    )
    repo.put_escalation(
        PROJECT_ID, "PROJ-123", "T001",
        {"reason": "scope_expansion", "resolved": True},
    )


def _make_event(
    story_id: str,
    project_id: str | None = None,
    sprint: str | None = None,
) -> dict:
    """Build a mock API Gateway event with path and query params."""
    params: dict[str, str] = {}
    if project_id is not None:
        params["project_id"] = project_id
    if sprint is not None:
        params["sprint"] = sprint
    return {
        "pathParameters": {"story_id": story_id},
        "queryStringParameters": params if params else None,
    }


class TestGetStoryDetailAC3:
    """AC-3: story PROJ-123 returns evidence, phase_durations, gates, escalations."""

    @mock_aws
    def test_returns_200_with_story(self) -> None:
        """Happy path — story exists, handler returns 200."""
        from src.handlers.get_story_detail import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_story(repo)

        result = handler(_make_event("PROJ-123", PROJECT_ID, "3"), None)

        assert result["statusCode"] == 200

    @mock_aws
    def test_response_has_story_fields(self) -> None:
        """Response includes story-level fields."""
        from src.handlers.get_story_detail import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_story(repo)

        result = handler(_make_event("PROJ-123", PROJECT_ID, "3"), None)
        body = json.loads(result["body"])

        assert body["story_id"] == "PROJ-123"
        assert body["status"] == "COMPLETE"
        assert body["cycle_time_days"] == 3.5

    @mock_aws
    def test_response_has_phase_durations(self) -> None:
        """Response includes phase_durations dict."""
        from src.handlers.get_story_detail import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_story(repo)

        result = handler(_make_event("PROJ-123", PROJECT_ID, "3"), None)
        body = json.loads(result["body"])

        assert body["phase_durations"] is not None
        assert body["phase_durations"]["phase_1_hours"] == 2.0

    @mock_aws
    def test_response_has_gate_timestamps(self) -> None:
        """Response includes gate_timestamps array."""
        from src.handlers.get_story_detail import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_story(repo)

        result = handler(_make_event("PROJ-123", PROJECT_ID, "3"), None)
        body = json.loads(result["body"])

        assert isinstance(body["gate_timestamps"], list)
        assert len(body["gate_timestamps"]) == 2
        assert body["gate_timestamps"][0]["gate"] == "G1"

    @mock_aws
    def test_response_has_escalation_log(self) -> None:
        """Response includes escalation_log array."""
        from src.handlers.get_story_detail import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_story(repo)

        result = handler(_make_event("PROJ-123", PROJECT_ID, "3"), None)
        body = json.loads(result["body"])

        assert isinstance(body["escalation_log"], list)
        assert len(body["escalation_log"]) == 1
        assert body["escalation_log"][0]["reason"] == "scope_expansion"

    @mock_aws
    def test_response_excludes_pk_sk(self) -> None:
        """DynamoDB keys PK and SK must not appear in response body."""
        from src.handlers.get_story_detail import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_story(repo)

        result = handler(_make_event("PROJ-123", PROJECT_ID, "3"), None)
        body = json.loads(result["body"])

        assert "PK" not in body
        assert "SK" not in body
        if body["phase_durations"]:
            assert "PK" not in body["phase_durations"]
        for g in body["gate_timestamps"]:
            assert "PK" not in g
        for e in body["escalation_log"]:
            assert "PK" not in e

    @mock_aws
    def test_response_has_cors_headers(self) -> None:
        """Response must include CORS headers."""
        from src.handlers.get_story_detail import handler, repo

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)
        _seed_story(repo)

        result = handler(_make_event("PROJ-123", PROJECT_ID, "3"), None)

        assert result["headers"]["Access-Control-Allow-Origin"] == "*"


class TestGetStoryDetailAC4:
    """AC-4: story PROJ-999 not found returns 404 STORY_NOT_FOUND."""

    @mock_aws
    def test_returns_404_when_story_not_found(self) -> None:
        """Non-existent story — handler returns 404."""
        from src.handlers.get_story_detail import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        result = handler(_make_event("PROJ-999", PROJECT_ID, "3"), None)

        assert result["statusCode"] == 404
        body = json.loads(result["body"])
        assert body["error"] == "STORY_NOT_FOUND"

    @mock_aws
    def test_404_message_includes_story_id(self) -> None:
        """404 message includes the requested story_id."""
        from src.handlers.get_story_detail import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        result = handler(_make_event("PROJ-999", PROJECT_ID, "3"), None)
        body = json.loads(result["body"])

        assert "PROJ-999" in body["message"]


class TestGetStoryDetailValidation:
    """Validation: missing project_id or invalid sprint returns 400."""

    @mock_aws
    def test_returns_400_when_project_id_missing(self) -> None:
        """No project_id — handler returns 400."""
        from src.handlers.get_story_detail import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        event: dict = {
            "pathParameters": {"story_id": "PROJ-123"},
            "queryStringParameters": None,
        }
        result = handler(event, None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"] == "INVALID_PROJECT_ID"

    @mock_aws
    def test_returns_400_when_sprint_not_integer(self) -> None:
        """Non-integer sprint — handler returns 400."""
        from src.handlers.get_story_detail import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        result = handler(_make_event("PROJ-123", PROJECT_ID, "abc"), None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"] == "INVALID_SPRINT_NUM"

    @mock_aws
    def test_returns_400_when_sprint_missing(self) -> None:
        """Missing sprint param — handler returns 400."""
        from src.handlers.get_story_detail import handler

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(dynamodb)

        event: dict = {
            "pathParameters": {"story_id": "PROJ-123"},
            "queryStringParameters": {"project_id": PROJECT_ID},
        }
        result = handler(event, None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"] == "INVALID_SPRINT_NUM"
