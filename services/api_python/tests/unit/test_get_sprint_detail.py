"""
Unit tests for get_sprint_detail Lambda handler.
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

from src.repository.keys import pk, sk_sprint_summary, sk_story
from src.repository.metrics_repository import MetricsRepository

TABLE_NAME = "yooti-metrics"
PROJECT_ID = "yooti-ri"


@pytest.fixture(autouse=True)
def aws_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set required env vars for every test."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("TABLE_NAME", TABLE_NAME)


def _create_table(dynamodb: object) -> object:
    """Create the yooti-metrics table."""
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


def _seed_sprint_with_detail(table: object, sprint_num: int) -> None:
    """Seed a sprint summary with KPIs, breakdowns, and stories."""
    table.put_item(
        Item={
            "PK": pk(PROJECT_ID),
            "SK": sk_sprint_summary(sprint_num),
            "sprint_num": sprint_num,
            "project_id": PROJECT_ID,
            "cycle_time_avg_days": Decimal("3.5"),
            "sprint_completion_pct": Decimal("85.0"),
            "stories_shipped": 5,
            "stories_committed": 6,
            "phase_avg_hrs": {
                "requirements": Decimal("2.1"),
                "design": Decimal("1.5"),
                "implementation": Decimal("8.3"),
                "review": Decimal("1.2"),
            },
            "gate_rejection_rates": {
                "G1": Decimal("0.05"),
                "G2": Decimal("0.10"),
                "G3": Decimal("0.15"),
            },
            "escalation_breakdown": {
                "scope_error": 1,
                "spec_ambiguity": 2,
                "env_error": 0,
            },
        }
    )
    # Seed two stories
    for story_id in ["DASH-010", "DASH-011"]:
        table.put_item(
            Item={
                "PK": pk(PROJECT_ID),
                "SK": sk_story(sprint_num, story_id),
                "sprint_num": sprint_num,
                "project_id": PROJECT_ID,
                "story_id": story_id,
                "cycle_time_days": Decimal("3.0"),
                "status": "complete",
            }
        )


def _make_event(sprint_num: str, project_id: str = PROJECT_ID) -> dict:
    """Build an API Gateway event for sprint detail."""
    return {
        "pathParameters": {"sprint_num": sprint_num},
        "queryStringParameters": {"project_id": project_id},
    }


@mock_aws
def test_sprint_detail_returns_summary_and_stories() -> None:
    """AC-2: sprint detail returns summary KPIs, breakdowns, and stories."""
    import importlib
    import src.repository.metrics_repository as repo_mod

    repo_mod._dynamodb_resource = None

    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = _create_table(dynamodb)
    _seed_sprint_with_detail(table, 10)

    repo_mod._dynamodb_resource = dynamodb

    import src.handlers.get_sprint_detail as handler_mod

    importlib.reload(handler_mod)
    handler_mod.repo = MetricsRepository(dynamodb_resource=dynamodb)

    result = handler_mod.handler(_make_event("10"), None)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])

    assert body["sprint_num"] == 10
    assert "summary" in body
    assert body["summary"]["stories_shipped"] == 5
    assert "phase_avg_hrs" in body
    assert "gate_rejection_rates" in body
    assert "escalation_breakdown" in body
    assert len(body["stories"]) == 2


@mock_aws
def test_sprint_detail_strips_dynamo_keys() -> None:
    """PK and SK are stripped from summary and stories."""
    import importlib
    import src.repository.metrics_repository as repo_mod

    repo_mod._dynamodb_resource = None

    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = _create_table(dynamodb)
    _seed_sprint_with_detail(table, 10)

    repo_mod._dynamodb_resource = dynamodb

    import src.handlers.get_sprint_detail as handler_mod

    importlib.reload(handler_mod)
    handler_mod.repo = MetricsRepository(dynamodb_resource=dynamodb)

    result = handler_mod.handler(_make_event("10"), None)
    body = json.loads(result["body"])

    assert "PK" not in body["summary"]
    assert "SK" not in body["summary"]
    for story in body["stories"]:
        assert "PK" not in story
        assert "SK" not in story


@mock_aws
def test_sprint_not_found_returns_404() -> None:
    """AC-3: sprint 99 not found returns 404 SPRINT_NOT_FOUND."""
    import importlib
    import src.repository.metrics_repository as repo_mod

    repo_mod._dynamodb_resource = None

    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    _create_table(dynamodb)

    repo_mod._dynamodb_resource = dynamodb

    import src.handlers.get_sprint_detail as handler_mod

    importlib.reload(handler_mod)
    handler_mod.repo = MetricsRepository(dynamodb_resource=dynamodb)

    result = handler_mod.handler(_make_event("99"), None)

    assert result["statusCode"] == 404
    body = json.loads(result["body"])
    assert body["error"] == "SPRINT_NOT_FOUND"


@mock_aws
def test_invalid_sprint_num_string_returns_400() -> None:
    """AC-4: sprint_num 'abc' returns 400 INVALID_SPRINT_NUM."""
    import importlib
    import src.handlers.get_sprint_detail as handler_mod

    importlib.reload(handler_mod)

    event = {
        "pathParameters": {"sprint_num": "abc"},
        "queryStringParameters": {"project_id": PROJECT_ID},
    }
    result = handler_mod.handler(event, None)

    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert body["error"] == "INVALID_SPRINT_NUM"


@mock_aws
def test_invalid_sprint_num_zero_returns_400() -> None:
    """AC-4: sprint_num 0 returns 400 INVALID_SPRINT_NUM."""
    import importlib
    import src.handlers.get_sprint_detail as handler_mod

    importlib.reload(handler_mod)

    result = handler_mod.handler(_make_event("0"), None)

    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert body["error"] == "INVALID_SPRINT_NUM"


@mock_aws
def test_invalid_sprint_num_negative_returns_400() -> None:
    """AC-4: sprint_num -1 returns 400 INVALID_SPRINT_NUM."""
    import importlib
    import src.handlers.get_sprint_detail as handler_mod

    importlib.reload(handler_mod)

    result = handler_mod.handler(_make_event("-1"), None)

    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert body["error"] == "INVALID_SPRINT_NUM"


@mock_aws
def test_missing_project_id_returns_400() -> None:
    """Missing project_id returns 400."""
    import importlib
    import src.handlers.get_sprint_detail as handler_mod

    importlib.reload(handler_mod)

    event = {
        "pathParameters": {"sprint_num": "10"},
        "queryStringParameters": {},
    }
    result = handler_mod.handler(event, None)

    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert body["error"] == "INVALID_PROJECT_ID"
