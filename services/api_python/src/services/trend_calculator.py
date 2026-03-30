"""Compute delta_from_prev and direction for trend series."""
from decimal import Decimal
from typing import Any


def enrich_trend_series(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add delta_from_prev and direction to each trend point.

    Points must be sorted ascending by sprint_num.
    direction: "up" if value increased, "down" if decreased, "flat" if same.
    """
    sorted_points = sorted(points, key=lambda p: p["sprint_num"])
    enriched: list[dict[str, Any]] = []
    for i, point in enumerate(sorted_points):
        value = point.get("value", Decimal("0"))
        if i == 0:
            delta = Decimal("0")
            direction = "flat"
        else:
            prev_value = sorted_points[i - 1].get("value", Decimal("0"))
            delta = value - prev_value
            if delta > 0:
                direction = "up"
            elif delta < 0:
                direction = "down"
            else:
                direction = "flat"
        enriched.append({
            **point,
            "delta_from_prev": delta,
            "direction": direction,
        })
    return enriched
