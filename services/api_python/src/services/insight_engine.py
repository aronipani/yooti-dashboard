"""
Insight alert engine for yooti-dashboard.

Computes threshold-based alerts from sprint summary data.
Alerts are computed at ingest time — not at query time (D3).
Alert shape matches ARCH-DASHBOARD.md Section 3.
"""
from decimal import Decimal
from typing import Any


# Thresholds — configurable constants
BOTTLENECK_PHASE_HRS = Decimal("15")
HUMAN_VS_AGENT_MARGIN = Decimal("1.5")
CONSTITUTION_PASS_TARGET = Decimal("95")
COVERAGE_TARGET = Decimal("90")
REGRESSION_WARN = Decimal("5")
REGRESSION_SPIKE = Decimal("10")
ESCALATION_SPIKE = Decimal("15")
DEPLOY_FREQUENCY_TARGET = 2


def compute_alerts(summary: dict[str, Any]) -> list[dict[str, Any]]:
    """Compute insight alerts from sprint summary data.

    Returns list of alert dicts matching the insight_alert shape:
    { type, severity, message, metric, value, threshold }
    """
    alerts: list[dict[str, Any]] = []

    # BOTTLENECK — any phase_avg_hrs value exceeds threshold
    phase_avg = summary.get("phase_avg_hrs", {})
    if isinstance(phase_avg, dict):
        for phase_name, hrs in phase_avg.items():
            hrs_val = _to_decimal(hrs)
            if hrs_val > BOTTLENECK_PHASE_HRS:
                alerts.append({
                    "type": "BOTTLENECK",
                    "severity": "warn",
                    "message": (
                        f"{phase_name} ({float(hrs_val)}h) "
                        f"exceeds target ({float(BOTTLENECK_PHASE_HRS)}h). "
                        f"Consider Stage 4."
                    ),
                    "metric": f"{phase_name}_hrs",
                    "value": float(hrs_val),
                    "threshold": float(BOTTLENECK_PHASE_HRS),
                })

    # HUMAN_VS_AGENT — human_wait > agent_exec * margin
    human_wait = _to_decimal(summary.get("human_wait_hrs_avg", 0))
    agent_exec = _to_decimal(summary.get("agent_exec_hrs_avg", 0))
    if agent_exec > 0 and human_wait > agent_exec * HUMAN_VS_AGENT_MARGIN:
        alerts.append({
            "type": "HUMAN_VS_AGENT",
            "severity": "warn",
            "message": (
                f"Human wait ({float(human_wait)}h) exceeds "
                f"{float(HUMAN_VS_AGENT_MARGIN)}x agent exec ({float(agent_exec)}h). "
                f"Review gate turnaround times."
            ),
            "metric": "human_wait_hrs_avg",
            "value": float(human_wait),
            "threshold": float(agent_exec * HUMAN_VS_AGENT_MARGIN),
        })

    # CONSTITUTION_GAP — constitution_pass_pct < 95%
    constitution_pct = _to_decimal(summary.get("constitution_pass_pct", 100))
    if constitution_pct < CONSTITUTION_PASS_TARGET:
        alerts.append({
            "type": "CONSTITUTION_GAP",
            "severity": "critical",
            "message": (
                f"Constitution pass rate ({float(constitution_pct)}%) "
                f"below target ({float(CONSTITUTION_PASS_TARGET)}%)."
            ),
            "metric": "constitution_pass_pct",
            "value": float(constitution_pct),
            "threshold": float(CONSTITUTION_PASS_TARGET),
        })

    # QUALITY_DROP — coverage < 90% or regression > 5%
    coverage = _to_decimal(summary.get("coverage_new_code_avg", 100))
    if coverage < COVERAGE_TARGET:
        alerts.append({
            "type": "QUALITY_DROP",
            "severity": "warn",
            "message": (
                f"New code coverage ({float(coverage)}%) "
                f"below target ({float(COVERAGE_TARGET)}%)."
            ),
            "metric": "coverage_new_code_avg",
            "value": float(coverage),
            "threshold": float(COVERAGE_TARGET),
        })

    regression = _to_decimal(summary.get("regression_rate_pct", 0))
    if regression > REGRESSION_WARN:
        alerts.append({
            "type": "QUALITY_DROP",
            "severity": "warn",
            "message": (
                f"Regression rate ({float(regression)}%) "
                f"exceeds warning threshold ({float(REGRESSION_WARN)}%)."
            ),
            "metric": "regression_rate_pct",
            "value": float(regression),
            "threshold": float(REGRESSION_WARN),
        })

    # REGRESSION_SPIKE — regression > 10%
    if regression > REGRESSION_SPIKE:
        alerts.append({
            "type": "REGRESSION_SPIKE",
            "severity": "critical",
            "message": (
                f"Regression rate ({float(regression)}%) "
                f"exceeds spike threshold ({float(REGRESSION_SPIKE)}%)."
            ),
            "metric": "regression_rate_pct",
            "value": float(regression),
            "threshold": float(REGRESSION_SPIKE),
        })

    # ESCALATION_SPIKE — escalation > 15%
    escalation = _to_decimal(summary.get("escalation_rate_pct", 0))
    if escalation > ESCALATION_SPIKE:
        alerts.append({
            "type": "ESCALATION_SPIKE",
            "severity": "warn",
            "message": (
                f"Escalation rate ({float(escalation)}%) "
                f"exceeds threshold ({float(ESCALATION_SPIKE)}%)."
            ),
            "metric": "escalation_rate_pct",
            "value": float(escalation),
            "threshold": float(ESCALATION_SPIKE),
        })

    # DORA_GAP — deploy frequency below target
    deploy_freq = summary.get("deploy_frequency", DEPLOY_FREQUENCY_TARGET)
    if isinstance(deploy_freq, (int, float, Decimal)):
        if int(deploy_freq) < DEPLOY_FREQUENCY_TARGET:
            alerts.append({
                "type": "DORA_GAP",
                "severity": "warn",
                "message": (
                    f"Deploy frequency ({deploy_freq}) "
                    f"below target ({DEPLOY_FREQUENCY_TARGET})."
                ),
                "metric": "deploy_frequency",
                "value": int(deploy_freq),
                "threshold": DEPLOY_FREQUENCY_TARGET,
            })

    return alerts


def _to_decimal(value: Any) -> Decimal:
    """Convert a value to Decimal safely."""
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0")
