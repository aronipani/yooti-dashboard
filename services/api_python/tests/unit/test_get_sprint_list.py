"""
Unit tests for get_sprint_list Lambda handler.
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

from src.repository.keys import pk, sk_sprint_summary
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


def _seed_sprint(table: object, sprint_num: int) -> None:
    """Seed a sprint summary record."""
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
        }
    )


@mock_aws
def test_five_sprints_returned_descending() -> None:
    """AC-1: five sprints returns array of five summaries in descending order."""
    import importlib
    import src.repository.metrics_repository as repo_mod

    repo_mod._dynamodb_resource = None

    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = _create_table(dynamodb)

    for num in [1, 2, 3, 4, 5]:
        _seed_sprint(table, num)

    repo_mod._dynamodb_resource = dynamodb

    import src.handlers.get_sprint_list as handler_mod

    importlib.reload(handler_mod)
    handler_mod.repo = MetricsRepository(dynamodb_resource=dynamodb)

    event = {"queryStringParameters": {"project_id": PROJECT_ID}}
    result = handler_mod.handler(event, None)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    sprints = body["sprints"]
    assert len(sprints) == 5
    nums = [s["sprint_num"] for s in sprints]
    assert nums == [5, 4, 3, 2, 1]


@mock_aws
def test_sprints_do_not_contain_dynamo_keys() -> None:
    """PK and SK are stripped from the response."""
    import importlib
    import src.repository.metrics_repository as repo_mod

    repo_mod._dynamodb_resource = None

    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = _create_table(dynamodb)
    _seed_sprint(table, 1)

    repo_mod._dynamodb_resource = dynamodb

    import src.handlers.get_sprint_list as handler_mod

    importlib.reload(handler_mod)
    handler_mod.repo = MetricsRepository(dynamodb_resource=dynamodb)

    event = {"queryStringParameters": {"project_id": PROJECT_ID}}
    result = handler_mod.handler(event, None)

    body = json.loads(result["body"])
    for sprint in body["sprints"]:
        assert "PK" not in sprint
        assert "SK" not in sprint


@mock_aws
def test_missing_project_id_returns_400() -> None:
    """Missing project_id query parameter returns 400."""
    import importlib
    import src.handlers.get_sprint_list as handler_mod

    importlib.reload(handler_mod)

    event = {"queryStringParameters": {}}
    result = handler_mod.handler(event, None)

    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert body["error"] == "INVALID_PROJECT_ID"


@mock_aws
def test_null_query_string_returns_400() -> None:
    """Null queryStringParameters returns 400."""
    import importlib
    import src.handlers.get_sprint_list as handler_mod

    importlib.reload(handler_mod)

    event = {"queryStringParameters": None}
    result = handler_mod.handler(event, None)

    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert body["error"] == "INVALID_PROJECT_ID"


@mock_aws
def test_empty_project_returns_empty_array() -> None:
    """A project with no sprints returns an empty array."""
    import importlib
    import src.repository.metrics_repository as repo_mod

    repo_mod._dynamodb_resource = None

    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    _create_table(dynamodb)

    repo_mod._dynamodb_resource = dynamodb

    import src.handlers.get_sprint_list as handler_mod

    importlib.reload(handler_mod)
    handler_mod.repo = MetricsRepository(dynamodb_resource=dynamodb)

    event = {"queryStringParameters": {"project_id": PROJECT_ID}}
    result = handler_mod.handler(event, None)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["sprints"] == []
