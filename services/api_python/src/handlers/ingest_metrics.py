"""
Lambda handler for POST /metrics/ingest.
Writes pipeline data to DynamoDB and updates CURRENT#SNAPSHOT.
Idempotent — safe to call multiple times for the same sprint.
"""
import json
from decimal import Decimal
from typing import Any

import structlog

from src.handlers.response import error, success
from src.repository.errors import RepositoryError
from src.repository.metrics_repository import MetricsRepository
from src.services.insight_engine import compute_alerts
from src.validators.ingest_validator import validate_ingest_payload

log = structlog.get_logger()

# Module-level — reused across invocations
repo = MetricsRepository()


def _convert_floats(obj: Any) -> Any:
    """Recursively convert float values to Decimal for DynamoDB compatibility."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _convert_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_floats(item) for item in obj]
    return obj


def handler(event: dict, context: Any) -> dict:
    """POST /metrics/ingest — write sprint data to DynamoDB."""
    log.info("handler.ingest_metrics")
    try:
        # Parse body — always json.loads, never assume dict
        raw_body = event.get("body") or "{}"
        try:
            body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        except (json.JSONDecodeError, TypeError):
            return error(400, "INVALID_BODY", "Request body must be valid JSON")

        # Validate
        data, err_code = validate_ingest_payload(body)
        if data is None:
            messages = {
                "INVALID_PROJECT_ID": "project_id is required",
                "INVALID_SPRINT_NUM": "sprint_num must be a positive integer",
                "INVALID_STORIES": "stories must be an array",
            }
            return error(400, err_code, messages.get(err_code, "Invalid input"))

        # Convert floats to Decimal for DynamoDB compatibility
        data = _convert_floats(data)

        project_id = data["project_id"]
        sprint_num = data["sprint_num"]
        stories = data["stories"]

        # Check if this is a re-ingest (sprint already exists)
        existing = repo.get_sprint_summary(project_id, sprint_num)
        is_re_ingest = existing is not None

        # Build and write sprint payload
        payload = {
            "summary": _build_summary(data),
            "stories": stories,
            "trends": _build_trends(data),
        }
        repo.batch_write_sprint(project_id, sprint_num, payload)

        # AC-5: Compute insight alerts and update CURRENT#SNAPSHOT
        import datetime
        summary = payload["summary"]
        alerts = compute_alerts(summary)
        # Convert floats in alerts to Decimal for DynamoDB
        alerts = _convert_floats(alerts)
        snapshot = {
            **summary,
            "sprint_num": sprint_num,
            "last_ingested_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "insight_alerts": alerts,
        }
        repo.put_current_snapshot(project_id, snapshot)

        status_code = 200 if is_re_ingest else 201
        return success(status_code, {
            "sprint_num": sprint_num,
            "stories_ingested": len(stories),
        })

    except RepositoryError:
        return error(500, "INTERNAL_ERROR", "An internal error occurred")
    except Exception:
        return error(500, "INTERNAL_ERROR", "An internal error occurred")


def _build_summary(data: dict[str, Any]) -> dict[str, Any]:
    """Extract summary fields from ingest payload."""
    summary_fields = [
        "cycle_time_avg_days", "sprint_completion_pct", "agent_exec_hrs_avg",
        "human_wait_hrs_avg", "deploy_frequency", "stories_shipped",
        "stories_committed", "coverage_new_code_avg", "mutation_score_avg",
        "regression_rate_pct", "constitution_pass_pct", "escalation_rate_pct",
        "iteration_avg", "correction_rate_pct", "gate_rejection_rates",
        "escalation_breakdown", "phase_avg_hrs",
    ]
    summary: dict[str, Any] = {}
    for field in summary_fields:
        if field in data:
            summary[field] = data[field]
    return summary


def _build_trends(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Build trend points from summary KPI fields."""
    from decimal import Decimal

    trend_metrics = [
        "cycle_time_avg_days", "sprint_completion_pct", "coverage_new_code_avg",
        "regression_rate_pct", "escalation_rate_pct", "deploy_frequency",
    ]
    trends = []
    for metric in trend_metrics:
        if metric in data:
            value = data[metric]
            if not isinstance(value, Decimal):
                value = Decimal(str(value))
            trends.append({"metric_name": metric, "value": value})
    return trends
