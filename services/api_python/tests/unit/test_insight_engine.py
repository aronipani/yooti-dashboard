"""
Unit tests for insight alert engine.
Tests each alert type with threshold boundary conditions.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from decimal import Decimal

from src.services.insight_engine import compute_alerts


class TestBottleneckAlert:
    def test_triggers_when_phase_exceeds_threshold(self) -> None:
        summary = {"phase_avg_hrs": {"g3_wait": Decimal("19")}}
        alerts = compute_alerts(summary)
        bottlenecks = [a for a in alerts if a["type"] == "BOTTLENECK"]
        assert len(bottlenecks) == 1
        assert bottlenecks[0]["severity"] == "warn"

    def test_does_not_trigger_when_below_threshold(self) -> None:
        summary = {"phase_avg_hrs": {"g3_wait": Decimal("10")}}
        alerts = compute_alerts(summary)
        bottlenecks = [a for a in alerts if a["type"] == "BOTTLENECK"]
        assert len(bottlenecks) == 0


class TestHumanVsAgentAlert:
    def test_triggers_when_human_wait_exceeds_margin(self) -> None:
        summary = {
            "human_wait_hrs_avg": Decimal("20"),
            "agent_exec_hrs_avg": Decimal("10"),
        }
        alerts = compute_alerts(summary)
        hvsa = [a for a in alerts if a["type"] == "HUMAN_VS_AGENT"]
        assert len(hvsa) == 1

    def test_does_not_trigger_when_within_margin(self) -> None:
        summary = {
            "human_wait_hrs_avg": Decimal("14"),
            "agent_exec_hrs_avg": Decimal("10"),
        }
        alerts = compute_alerts(summary)
        hvsa = [a for a in alerts if a["type"] == "HUMAN_VS_AGENT"]
        assert len(hvsa) == 0


class TestConstitutionGapAlert:
    def test_triggers_when_below_95(self) -> None:
        summary = {"constitution_pass_pct": Decimal("90")}
        alerts = compute_alerts(summary)
        gaps = [a for a in alerts if a["type"] == "CONSTITUTION_GAP"]
        assert len(gaps) == 1
        assert gaps[0]["severity"] == "critical"

    def test_does_not_trigger_at_95(self) -> None:
        summary = {"constitution_pass_pct": Decimal("95")}
        alerts = compute_alerts(summary)
        gaps = [a for a in alerts if a["type"] == "CONSTITUTION_GAP"]
        assert len(gaps) == 0


class TestQualityDropAlert:
    def test_triggers_on_low_coverage(self) -> None:
        summary = {"coverage_new_code_avg": Decimal("75")}
        alerts = compute_alerts(summary)
        drops = [a for a in alerts if a["type"] == "QUALITY_DROP"]
        assert len(drops) >= 1

    def test_triggers_on_high_regression(self) -> None:
        summary = {"regression_rate_pct": Decimal("7")}
        alerts = compute_alerts(summary)
        drops = [a for a in alerts if a["type"] == "QUALITY_DROP"]
        assert len(drops) == 1


class TestRegressionSpikeAlert:
    def test_triggers_above_10(self) -> None:
        summary = {"regression_rate_pct": Decimal("12")}
        alerts = compute_alerts(summary)
        spikes = [a for a in alerts if a["type"] == "REGRESSION_SPIKE"]
        assert len(spikes) == 1
        assert spikes[0]["severity"] == "critical"

    def test_does_not_trigger_at_10(self) -> None:
        summary = {"regression_rate_pct": Decimal("10")}
        alerts = compute_alerts(summary)
        spikes = [a for a in alerts if a["type"] == "REGRESSION_SPIKE"]
        assert len(spikes) == 0


class TestEscalationSpikeAlert:
    def test_triggers_above_15(self) -> None:
        summary = {"escalation_rate_pct": Decimal("20")}
        alerts = compute_alerts(summary)
        spikes = [a for a in alerts if a["type"] == "ESCALATION_SPIKE"]
        assert len(spikes) == 1

    def test_does_not_trigger_at_15(self) -> None:
        summary = {"escalation_rate_pct": Decimal("15")}
        alerts = compute_alerts(summary)
        spikes = [a for a in alerts if a["type"] == "ESCALATION_SPIKE"]
        assert len(spikes) == 0


class TestDoraGapAlert:
    def test_triggers_when_deploy_frequency_below_target(self) -> None:
        summary = {"deploy_frequency": 1}
        alerts = compute_alerts(summary)
        gaps = [a for a in alerts if a["type"] == "DORA_GAP"]
        assert len(gaps) == 1

    def test_does_not_trigger_at_target(self) -> None:
        summary = {"deploy_frequency": 2}
        alerts = compute_alerts(summary)
        gaps = [a for a in alerts if a["type"] == "DORA_GAP"]
        assert len(gaps) == 0


class TestNoAlerts:
    def test_returns_empty_for_healthy_sprint(self) -> None:
        summary = {
            "phase_avg_hrs": {"g3_wait": Decimal("10")},
            "human_wait_hrs_avg": Decimal("5"),
            "agent_exec_hrs_avg": Decimal("5"),
            "constitution_pass_pct": Decimal("100"),
            "coverage_new_code_avg": Decimal("95"),
            "regression_rate_pct": Decimal("0"),
            "escalation_rate_pct": Decimal("0"),
            "deploy_frequency": 3,
        }
        alerts = compute_alerts(summary)
        assert len(alerts) == 0

    def test_handles_empty_summary(self) -> None:
        alerts = compute_alerts({})
        assert isinstance(alerts, list)
