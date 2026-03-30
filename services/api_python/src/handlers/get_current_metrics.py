"""
Lambda handler for GET /metrics/current.
Returns current sprint snapshot for a project.
"""
import json
import os
from typing import Any

import structlog

from src.handlers.response import error, success
from src.repository.errors import RepositoryError
from src.repository.metrics_repository import MetricsRepository

log = structlog.get_logger()

# Module-level — reused across invocations
repo = MetricsRepository()


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """GET /metrics/current — returns current snapshot."""
    log.info("handler.get_current_metrics")
    try:
        params = event.get("queryStringParameters") or {}
        project_id = params.get("project_id", "").strip()

        if not project_id:
            return error(400, "INVALID_PROJECT_ID", "project_id is required")

        snapshot = repo.get_current_snapshot(project_id)
        if snapshot is None:
            return error(
                404,
                "SPRINT_NOT_FOUND",
                f"No current snapshot for project {project_id}",
            )

        # Remove internal DynamoDB keys from response
        snapshot.pop("PK", None)
        snapshot.pop("SK", None)

        return success(200, snapshot)
    except RepositoryError as exc:
        log.error("handler.repo_error", error=str(exc))
        return error(500, "INTERNAL_ERROR", f"Debug repo: {exc}")
    except Exception as exc:
        log.error("handler.unhandled_error", error=str(exc), error_type=type(exc).__name__)
        return error(500, "INTERNAL_ERROR", f"Debug: {type(exc).__name__}: {exc}")
