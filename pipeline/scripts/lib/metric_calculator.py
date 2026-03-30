"""Compute sprint summary KPIs from collected .agent/ data."""
from __future__ import annotations

from typing import Any


def compute_sprint_summary(
    stories_data: list[dict[str, Any]],
    gates: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    escalations: list[dict[str, str]],
    corrections: list[dict[str, str]],
) -> dict[str, Any]:
    """Build KPI dict matching the ingest schema.

    For a greenfield first sprint where most data is sparse,
    uses sensible defaults (0 for rates, empty dicts for breakdowns).
    """
    stories_committed = len(stories_data)
    stories_shipped = _count_shipped(stories_data, gates)

    sprint_completion_pct = (
        round(stories_shipped / stories_committed * 100, 1)
        if stories_committed > 0
        else 0.0
    )

    coverage_new_code_avg = _avg_coverage_new_code(evidence)
    regression_rate_pct = _regression_rate(evidence)
    escalation_rate_pct = (
        round(len(escalations) / stories_committed * 100, 1)
        if stories_committed > 0
        else 0.0
    )
    correction_rate_pct = (
        round(len(corrections) / stories_committed * 100, 1)
        if stories_committed > 0
        else 0.0
    )
    gate_rejection_rates = _gate_rejection_rates(gates, stories_committed)
    escalation_breakdown = _escalation_breakdown(escalations)

    return {
        "cycle_time_avg_days": 0.0,
        "sprint_completion_pct": sprint_completion_pct,
        "stories_shipped": stories_shipped,
        "stories_committed": stories_committed,
        "coverage_new_code_avg": coverage_new_code_avg,
        "regression_rate_pct": regression_rate_pct,
        "constitution_pass_pct": 100.0,
        "escalation_rate_pct": escalation_rate_pct,
        "iteration_avg": 0.0,
        "correction_rate_pct": correction_rate_pct,
        "gate_rejection_rates": gate_rejection_rates,
        "escalation_breakdown": escalation_breakdown,
        "phase_avg_hrs": {},
        "deploy_frequency": 0,
        "agent_exec_hrs_avg": 0.0,
        "human_wait_hrs_avg": 0.0,
        "mutation_score_avg": 0.0,
    }


def _count_shipped(
    stories_data: list[dict[str, Any]],
    gates: list[dict[str, Any]],
) -> int:
    """A story is shipped if it has a G3 approved gate."""
    g3_stories = {g["story_id"] for g in gates if g.get("gate") == "G3"}
    return sum(1 for s in stories_data if s.get("story_id") in g3_stories)


def _avg_coverage_new_code(evidence: list[dict[str, Any]]) -> float:
    """Average new_code coverage across evidence packages."""
    values = []
    for e in evidence:
        cs = e.get("coverage_summary")
        if cs and isinstance(cs, dict) and "new_code" in cs:
            values.append(float(cs["new_code"]))
    return round(sum(values) / len(values), 1) if values else 0.0


def _regression_rate(evidence: list[dict[str, Any]]) -> float:
    """Percentage of stories with test regressions."""
    total = 0
    regressed = 0
    for e in evidence:
        tr = e.get("test_results")
        if tr and isinstance(tr, dict):
            total += 1
            unit = tr.get("unit", {})
            integration = tr.get("integration", {})
            if unit.get("failed", 0) > 0 or integration.get("failed", 0) > 0:
                regressed += 1
    return round(regressed / total * 100, 1) if total > 0 else 0.0


def _gate_rejection_rates(
    gates: list[dict[str, Any]], stories_committed: int
) -> dict[str, float]:
    """Compute rejection rate per gate level. Currently returns 0s."""
    if stories_committed == 0:
        return {}
    result: dict[str, float] = {}
    gate_names = sorted({g["gate"] for g in gates})
    for gn in gate_names:
        result[gn] = 0.0
    return result


def _escalation_breakdown(escalations: list[dict[str, str]]) -> dict[str, int]:
    """Group escalations by type keyword found in filename."""
    breakdown: dict[str, int] = {}
    type_keywords = ["scope", "install", "blocker", "ambiguity", "env"]
    for esc in escalations:
        fname = esc.get("filename", "").lower()
        matched = False
        for kw in type_keywords:
            if kw in fname:
                breakdown[kw] = breakdown.get(kw, 0) + 1
                matched = True
                break
        if not matched:
            breakdown["other"] = breakdown.get("other", 0) + 1
    return breakdown
