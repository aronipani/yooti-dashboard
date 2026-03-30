"""Lambda handler for GET /metrics/story/{story_id}."""
from typing import Any

import structlog

from src.handlers.response import error, success
from src.repository.errors import RepositoryError
from src.repository.metrics_repository import MetricsRepository

log = structlog.get_logger()
repo = MetricsRepository()


def handler(event: dict, context: Any) -> dict:
    """Return story detail with phase_durations, gate_timestamps, escalation_log."""
    log.info("handler.get_story_detail")
    try:
        path_params = event.get("pathParameters") or {}
        story_id = path_params.get("story_id", "").strip()

        params = event.get("queryStringParameters") or {}
        project_id = params.get("project_id", "").strip()
        raw_sprint = params.get("sprint", "")

        if not project_id:
            return error(400, "INVALID_PROJECT_ID", "project_id is required")

        try:
            sprint_num = int(raw_sprint)
        except (ValueError, TypeError):
            return error(
                400, "INVALID_SPRINT_NUM",
                "sprint is required and must be an integer",
            )

        story = repo.get_story_detail(project_id, sprint_num, story_id)
        if story is None:
            return error(
                404, "STORY_NOT_FOUND",
                f"Story {story_id} not found in sprint {sprint_num}",
            )

        phases = repo.get_phase_durations(project_id, sprint_num, story_id)
        gates = repo.get_gate_events(project_id, story_id)
        escalations = repo.get_escalations(project_id, story_id)

        # Clean DynamoDB keys
        story.pop("PK", None)
        story.pop("SK", None)
        if phases:
            phases.pop("PK", None)
            phases.pop("SK", None)
        for g in gates:
            g.pop("PK", None)
            g.pop("SK", None)
        for e in escalations:
            e.pop("PK", None)
            e.pop("SK", None)

        body: dict[str, Any] = {
            **story,
            "phase_durations": phases,
            "gate_timestamps": gates,
            "escalation_log": escalations,
        }
        return success(200, body)
    except RepositoryError:
        return error(500, "INTERNAL_ERROR", "An internal error occurred")
    except Exception:
        return error(500, "INTERNAL_ERROR", "An internal error occurred")
