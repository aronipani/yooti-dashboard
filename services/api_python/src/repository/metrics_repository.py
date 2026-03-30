"""
DynamoDB repository for yooti-metrics dashboard.

Single-table design. No Scan operations permitted.
All reads use Query or GetItem. All writes use PutItem or BatchWriteItem.
TABLE_NAME loaded from os.environ at module level.
"""
import json
import os
from decimal import Decimal
from typing import Any, Optional

import boto3
import structlog
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from . import errors
from . import keys

log = structlog.get_logger()

TABLE_NAME = os.environ.get("TABLE_NAME", "yooti-metrics")

_dynamodb_resource: Optional[Any] = None


def _get_dynamodb_resource() -> Any:
    """Get or create the module-level DynamoDB resource."""
    global _dynamodb_resource
    if _dynamodb_resource is None:
        endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
        _dynamodb_resource = boto3.resource(
            "dynamodb",
            endpoint_url=endpoint_url,
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
        )
    return _dynamodb_resource


class MetricsRepository:
    """Repository for all yooti-metrics DynamoDB operations.

    All methods catch ClientError and raise RepositoryError.
    No Scan operations anywhere. All reads use GetItem or Query.
    """

    def __init__(self, dynamodb_resource: Optional[Any] = None) -> None:
        """Initialise with optional DynamoDB resource for testability."""
        self._resource = dynamodb_resource
        self._table_ref: Optional[Any] = None

    @property
    def _table(self) -> Any:
        """Lazy table reference using TABLE_NAME from os.environ."""
        if self._table_ref is None:
            resource = self._resource or _get_dynamodb_resource()
            self._table_ref = resource.Table(TABLE_NAME)
        return self._table_ref

    def _handle_client_error(self, operation: str, err: ClientError) -> None:
        """Convert ClientError to RepositoryError — no internal detail exposed."""
        log.error(
            "repository.error",
            operation=operation,
            error_code=err.response["Error"]["Code"],
        )
        raise errors.RepositoryError(
            f"Repository operation failed: {operation}"
        ) from err

    # ── Read methods ─────────────────────────────────────────

    def get_current_snapshot(self, project_id: str) -> Optional[dict[str, Any]]:
        """Fetch current snapshot using single GetItem — AP-1."""
        log.info("repository.get_current_snapshot", project_id=project_id)
        try:
            response = self._table.get_item(
                Key={"PK": keys.pk(project_id), "SK": keys.sk_current_snapshot()}
            )
            return response.get("Item")
        except ClientError as err:
            self._handle_client_error("get_current_snapshot", err)
            return None  # unreachable — _handle_client_error always raises

    def get_sprint_summary(
        self, project_id: str, sprint_num: int
    ) -> Optional[dict[str, Any]]:
        """Fetch sprint summary using GetItem — AP-3."""
        log.info(
            "repository.get_sprint_summary",
            project_id=project_id,
            sprint_num=sprint_num,
        )
        try:
            response = self._table.get_item(
                Key={
                    "PK": keys.pk(project_id),
                    "SK": keys.sk_sprint_summary(sprint_num),
                }
            )
            return response.get("Item")
        except ClientError as err:
            self._handle_client_error("get_sprint_summary", err)
            return None

    def get_sprint_stories(
        self, project_id: str, sprint_num: int
    ) -> list[dict[str, Any]]:
        """Fetch all stories in a sprint using Query SK begins_with — AP-2."""
        log.info(
            "repository.get_sprint_stories",
            project_id=project_id,
            sprint_num=sprint_num,
        )
        try:
            response = self._table.query(
                KeyConditionExpression=(
                    Key("PK").eq(keys.pk(project_id))
                    & Key("SK").begins_with(keys.sk_story_prefix(sprint_num))
                )
            )
            return response.get("Items", [])
        except ClientError as err:
            self._handle_client_error("get_sprint_stories", err)
            return []

    def get_sprint_list(self, project_id: str) -> list[dict[str, Any]]:
        """Fetch all sprint summaries sorted descending — AP-4.

        Query with SK begins_with SPRINT# then filter for SUMMARY suffix.
        """
        log.info("repository.get_sprint_list", project_id=project_id)
        try:
            response = self._table.query(
                KeyConditionExpression=(
                    Key("PK").eq(keys.pk(project_id))
                    & Key("SK").begins_with(keys.SK_PREFIX_SPRINT)
                )
            )
            summaries = [
                item
                for item in response.get("Items", [])
                if item["SK"].endswith("#SUMMARY")
            ]
            summaries.sort(key=lambda x: x["sprint_num"], reverse=True)
            return summaries
        except ClientError as err:
            self._handle_client_error("get_sprint_list", err)
            return []

    def get_trends(
        self, project_id: str, metric: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Fetch trend series — AP-5 (single metric) or AP-6 (all metrics)."""
        log.info(
            "repository.get_trends", project_id=project_id, metric=metric
        )
        try:
            prefix = (
                keys.sk_trend_metric_prefix(metric)
                if metric
                else keys.SK_PREFIX_TREND
            )
            response = self._table.query(
                KeyConditionExpression=(
                    Key("PK").eq(keys.pk(project_id))
                    & Key("SK").begins_with(prefix)
                )
            )
            return response.get("Items", [])
        except ClientError as err:
            self._handle_client_error("get_trends", err)
            return []

    def get_story_detail(
        self, project_id: str, sprint_num: int, story_id: str
    ) -> Optional[dict[str, Any]]:
        """Fetch a single story's metrics using GetItem."""
        log.info(
            "repository.get_story_detail",
            project_id=project_id,
            sprint_num=sprint_num,
            story_id=story_id,
        )
        try:
            response = self._table.get_item(
                Key={
                    "PK": keys.pk(project_id),
                    "SK": keys.sk_story(sprint_num, story_id),
                }
            )
            return response.get("Item")
        except ClientError as err:
            self._handle_client_error("get_story_detail", err)
            return None

    def get_phase_durations(
        self, project_id: str, sprint_num: int, story_id: str
    ) -> Optional[dict[str, Any]]:
        """Fetch phase durations for a story using GetItem — AP-7."""
        log.info(
            "repository.get_phase_durations",
            project_id=project_id,
            sprint_num=sprint_num,
            story_id=story_id,
        )
        try:
            response = self._table.get_item(
                Key={
                    "PK": keys.pk(project_id),
                    "SK": keys.sk_phase(sprint_num, story_id),
                }
            )
            return response.get("Item")
        except ClientError as err:
            self._handle_client_error("get_phase_durations", err)
            return None

    def get_gate_events(
        self, project_id: str, story_id: str
    ) -> list[dict[str, Any]]:
        """Fetch all gate events for a story using Query begins_with — AP-8."""
        log.info(
            "repository.get_gate_events",
            project_id=project_id,
            story_id=story_id,
        )
        try:
            response = self._table.query(
                KeyConditionExpression=(
                    Key("PK").eq(keys.pk(project_id))
                    & Key("SK").begins_with(keys.sk_gate_prefix(story_id))
                )
            )
            return response.get("Items", [])
        except ClientError as err:
            self._handle_client_error("get_gate_events", err)
            return []

    def get_escalations(
        self, project_id: str, story_id: str
    ) -> list[dict[str, Any]]:
        """Fetch all escalations for a story using Query begins_with — AP-9."""
        log.info(
            "repository.get_escalations",
            project_id=project_id,
            story_id=story_id,
        )
        try:
            response = self._table.query(
                KeyConditionExpression=(
                    Key("PK").eq(keys.pk(project_id))
                    & Key("SK").begins_with(keys.sk_esc_prefix(story_id))
                )
            )
            return response.get("Items", [])
        except ClientError as err:
            self._handle_client_error("get_escalations", err)
            return []

    # ── Write methods ────────────────────────────────────────

    def put_sprint_summary(
        self, project_id: str, sprint_num: int, data: dict[str, Any]
    ) -> None:
        """Write sprint summary. Idempotent — overwrites on re-ingest."""
        log.info(
            "repository.put_sprint_summary",
            project_id=project_id,
            sprint_num=sprint_num,
        )
        try:
            item = {
                "PK": keys.pk(project_id),
                "SK": keys.sk_sprint_summary(sprint_num),
                "project_id": project_id,
                "sprint_num": sprint_num,
                **data,
            }
            self._table.put_item(Item=item)
        except ClientError as err:
            self._handle_client_error("put_sprint_summary", err)

    def put_story_metrics(
        self,
        project_id: str,
        sprint_num: int,
        story_id: str,
        data: dict[str, Any],
    ) -> None:
        """Write story metrics. Idempotent — overwrites on re-ingest."""
        log.info(
            "repository.put_story_metrics",
            project_id=project_id,
            story_id=story_id,
        )
        try:
            item = {
                "PK": keys.pk(project_id),
                "SK": keys.sk_story(sprint_num, story_id),
                "project_id": project_id,
                "sprint_num": sprint_num,
                "story_id": story_id,
                **data,
            }
            self._table.put_item(Item=item)
        except ClientError as err:
            self._handle_client_error("put_story_metrics", err)

    def put_phase_durations(
        self,
        project_id: str,
        sprint_num: int,
        story_id: str,
        data: dict[str, Any],
    ) -> None:
        """Write phase durations for a story."""
        log.info(
            "repository.put_phase_durations",
            project_id=project_id,
            story_id=story_id,
        )
        try:
            item = {
                "PK": keys.pk(project_id),
                "SK": keys.sk_phase(sprint_num, story_id),
                "project_id": project_id,
                "sprint_num": sprint_num,
                "story_id": story_id,
                **data,
            }
            self._table.put_item(Item=item)
        except ClientError as err:
            self._handle_client_error("put_phase_durations", err)

    def put_trend_point(
        self,
        project_id: str,
        metric_name: str,
        sprint_num: int,
        value: Decimal,
    ) -> None:
        """Write a single trend data point."""
        log.info(
            "repository.put_trend_point",
            project_id=project_id,
            metric_name=metric_name,
            sprint_num=sprint_num,
        )
        try:
            item = {
                "PK": keys.pk(project_id),
                "SK": keys.sk_trend(metric_name, sprint_num),
                "project_id": project_id,
                "metric_name": metric_name,
                "sprint_num": sprint_num,
                "value": value,
            }
            self._table.put_item(Item=item)
        except ClientError as err:
            self._handle_client_error("put_trend_point", err)

    def put_current_snapshot(
        self, project_id: str, data: dict[str, Any]
    ) -> None:
        """Write CURRENT#SNAPSHOT. Always overwrites — no conditional."""
        log.info(
            "repository.put_current_snapshot",
            project_id=project_id,
        )
        try:
            item = {
                "PK": keys.pk(project_id),
                "SK": keys.sk_current_snapshot(),
                "project_id": project_id,
                **data,
            }
            self._table.put_item(Item=item)
        except ClientError as err:
            self._handle_client_error("put_current_snapshot", err)

    def put_gate_event(
        self,
        project_id: str,
        story_id: str,
        gate_num: int,
        data: dict[str, Any],
    ) -> None:
        """Write a gate event record."""
        log.info(
            "repository.put_gate_event",
            project_id=project_id,
            story_id=story_id,
            gate=gate_num,
        )
        try:
            item = {
                "PK": keys.pk(project_id),
                "SK": keys.sk_gate(story_id, gate_num),
                "project_id": project_id,
                "story_id": story_id,
                "gate": f"G{gate_num}",
                **data,
            }
            self._table.put_item(Item=item)
        except ClientError as err:
            self._handle_client_error("put_gate_event", err)

    def put_escalation(
        self,
        project_id: str,
        story_id: str,
        task_id: str,
        data: dict[str, Any],
    ) -> None:
        """Write an escalation record."""
        log.info(
            "repository.put_escalation",
            project_id=project_id,
            story_id=story_id,
            task_id=task_id,
        )
        try:
            item = {
                "PK": keys.pk(project_id),
                "SK": keys.sk_escalation(story_id, task_id),
                "project_id": project_id,
                "story_id": story_id,
                "task_id": task_id,
                **data,
            }
            self._table.put_item(Item=item)
        except ClientError as err:
            self._handle_client_error("put_escalation", err)

    def batch_write_sprint(
        self,
        project_id: str,
        sprint_num: int,
        payload: dict[str, Any],
    ) -> None:
        """Write all entities for a sprint using individual PutItem calls.

        Idempotent — safe to call multiple times for the same sprint.
        Uses PutItem (not BatchWriteItem) to support items > 400KB and
        to keep error handling per-item.
        """
        log.info(
            "repository.batch_write_sprint",
            project_id=project_id,
            sprint_num=sprint_num,
        )
        # Write summary
        if "summary" in payload:
            self.put_sprint_summary(project_id, sprint_num, payload["summary"])

        # Write stories
        for story in payload.get("stories", []):
            story_id = story["story_id"]
            self.put_story_metrics(project_id, sprint_num, story_id, story)

        # Write trends
        for trend in payload.get("trends", []):
            self.put_trend_point(
                project_id,
                trend["metric_name"],
                sprint_num,
                trend["value"],
            )
