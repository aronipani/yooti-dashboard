"""Lambda handler for GET /metrics/sprint/{sprint_num}."""
from typing import Any

import structlog

from src.handlers.response import error, success
from src.repository.errors import RepositoryError
from src.repository.metrics_repository import MetricsRepository

log = structlog.get_logger()
repo = MetricsRepository()


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Return sprint detail including summary KPIs, breakdowns, and stories."""
    log.info("handler.get_sprint_detail")
    try:
        path_params = event.get("pathParameters") or {}
        raw_sprint = path_params.get("sprint_num", "")

        # Validate sprint_num is a positive integer
        try:
            sprint_num = int(raw_sprint)
            if sprint_num <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return error(
                400,
                "INVALID_SPRINT_NUM",
                f"sprint_num must be a positive integer, got: {raw_sprint}",
            )

        params = event.get("queryStringParameters") or {}
        project_id = params.get("project_id", "").strip()
        if not project_id:
            return error(400, "INVALID_PROJECT_ID", "project_id is required")

        summary = repo.get_sprint_summary(project_id, sprint_num)
        if summary is None:
            return error(404, "SPRINT_NOT_FOUND", f"Sprint {sprint_num} not found")

        stories = repo.get_sprint_stories(project_id, sprint_num)

        # Remove DynamoDB keys from response
        summary.pop("PK", None)
        summary.pop("SK", None)
        for s in stories:
            s.pop("PK", None)
            s.pop("SK", None)

        body = {
            "sprint_num": sprint_num,
            "summary": summary,
            "phase_avg_hrs": summary.get("phase_avg_hrs", {}),
            "gate_rejection_rates": summary.get("gate_rejection_rates", {}),
            "escalation_breakdown": summary.get("escalation_breakdown", {}),
            "stories": stories,
        }
        return success(200, body)
    except RepositoryError:
        return error(500, "INTERNAL_ERROR", "An internal error occurred")
    except Exception:
        return error(500, "INTERNAL_ERROR", "An internal error occurred")
