"""
Input validation for POST /metrics/ingest payload.
Returns (validated_data, error_list) tuple.
"""
from typing import Any


def validate_ingest_payload(
    body: dict[str, Any],
) -> tuple[dict[str, Any] | None, str | None]:
    """Validate the ingest payload structure.

    Returns (data, None) on success or (None, error_message) on failure.
    """
    project_id = body.get("project_id", "")
    if not isinstance(project_id, str) or not project_id.strip():
        return None, "INVALID_PROJECT_ID"

    sprint_num = body.get("sprint_num")
    if not isinstance(sprint_num, int) or sprint_num <= 0:
        return None, "INVALID_SPRINT_NUM"

    stories = body.get("stories")
    if not isinstance(stories, list):
        return None, "INVALID_STORIES"

    return body, None
