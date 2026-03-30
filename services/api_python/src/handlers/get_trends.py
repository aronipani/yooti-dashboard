"""Lambda handler for GET /metrics/trends."""
from typing import Any

import structlog

from src.handlers.response import error, success
from src.repository.errors import RepositoryError
from src.repository.metrics_repository import MetricsRepository
from src.services.trend_calculator import enrich_trend_series

log = structlog.get_logger()
repo = MetricsRepository()


def handler(event: dict, context: Any) -> dict:
    """Return trend series grouped by metric_name with delta and direction."""
    log.info("handler.get_trends")
    try:
        params = event.get("queryStringParameters") or {}
        project_id = params.get("project_id", "").strip()
        if not project_id:
            return error(400, "INVALID_PROJECT_ID", "project_id is required")

        metric = params.get("metric")
        items = repo.get_trends(project_id, metric=metric)

        # Remove DynamoDB keys
        for item in items:
            item.pop("PK", None)
            item.pop("SK", None)

        # Group by metric_name and enrich
        grouped: dict[str, list] = {}
        for item in items:
            name = item.get("metric_name", "unknown")
            grouped.setdefault(name, []).append(item)

        trends: dict[str, list] = {}
        for name, points in grouped.items():
            trends[name] = enrich_trend_series(points)

        return success(200, {"trends": trends})
    except RepositoryError:
        return error(500, "INTERNAL_ERROR", "An internal error occurred")
    except Exception:
        return error(500, "INTERNAL_ERROR", "An internal error occurred")
