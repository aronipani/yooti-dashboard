"""Lambda handler for GET /metrics/sprints."""
from typing import Any

import structlog

from src.handlers.response import error, success
from src.repository.errors import RepositoryError
from src.repository.metrics_repository import MetricsRepository

log = structlog.get_logger()
repo = MetricsRepository()


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Return all sprint summaries for a project in descending order."""
    log.info("handler.get_sprint_list")
    try:
        params = event.get("queryStringParameters") or {}
        project_id = params.get("project_id", "").strip()
        if not project_id:
            return error(400, "INVALID_PROJECT_ID", "project_id is required")

        sprints = repo.get_sprint_list(project_id)
        # Remove DynamoDB keys from response
        for s in sprints:
            s.pop("PK", None)
            s.pop("SK", None)
        return success(200, {"sprints": sprints})
    except RepositoryError:
        return error(500, "INTERNAL_ERROR", "An internal error occurred")
    except Exception:
        return error(500, "INTERNAL_ERROR", "An internal error occurred")
