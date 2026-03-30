"""Tests for metric_calculator module."""
from __future__ import annotations

from lib.metric_calculator import compute_sprint_summary


class TestComputeSprintSummary:
    def test_basic_computation(self) -> None:
        stories = [
            {"story_id": "DASH-001"},
            {"story_id": "DASH-002"},
        ]
        gates = [
            {"story_id": "DASH-001", "gate": "G2"},
            {"story_id": "DASH-001", "gate": "G3"},
            {"story_id": "DASH-002", "gate": "G2"},
        ]
        evidence = [
            {
                "story_id": "DASH-001",
                "test_results": {
                    "unit": {"total": 10, "passed": 10, "failed": 0},
                    "integration": {"total": 2, "passed": 2, "failed": 0},
                },
                "coverage_summary": {"overall": 85.0, "new_code": 92.5},
            },
        ]
        escalations = [{"filename": "DASH-002-scope.md", "content": "..."}]
        corrections = [{"filename": "DASH-001-T002-fix.md", "content": "..."}]

        result = compute_sprint_summary(stories, gates, evidence, escalations, corrections)

        assert result["stories_committed"] == 2
        assert result["stories_shipped"] == 1
        assert result["sprint_completion_pct"] == 50.0
        assert result["coverage_new_code_avg"] == 92.5
        assert result["regression_rate_pct"] == 0.0
        assert result["escalation_rate_pct"] == 50.0
        assert result["correction_rate_pct"] == 50.0
        assert result["constitution_pass_pct"] == 100.0

    def test_empty_data(self) -> None:
        result = compute_sprint_summary([], [], [], [], [])

        assert result["stories_committed"] == 0
        assert result["stories_shipped"] == 0
        assert result["sprint_completion_pct"] == 0.0
        assert result["coverage_new_code_avg"] == 0.0
        assert result["regression_rate_pct"] == 0.0
        assert result["escalation_rate_pct"] == 0.0
        assert result["correction_rate_pct"] == 0.0
        assert result["gate_rejection_rates"] == {}
        assert result["escalation_breakdown"] == {}

    def test_all_stories_shipped(self) -> None:
        stories = [{"story_id": "DASH-001"}]
        gates = [
            {"story_id": "DASH-001", "gate": "G2"},
            {"story_id": "DASH-001", "gate": "G3"},
        ]
        result = compute_sprint_summary(stories, gates, [], [], [])
        assert result["stories_shipped"] == 1
        assert result["sprint_completion_pct"] == 100.0

    def test_regression_detected(self) -> None:
        stories = [{"story_id": "DASH-001"}]
        evidence = [
            {
                "story_id": "DASH-001",
                "test_results": {
                    "unit": {"total": 10, "passed": 9, "failed": 1},
                    "integration": {"total": 2, "passed": 2, "failed": 0},
                },
                "coverage_summary": None,
            },
        ]
        result = compute_sprint_summary(stories, [], evidence, [], [])
        assert result["regression_rate_pct"] == 100.0

    def test_escalation_breakdown(self) -> None:
        escalations = [
            {"filename": "DASH-001-scope.md", "content": ""},
            {"filename": "DASH-002-scope.md", "content": ""},
            {"filename": "DASH-003-install-required.md", "content": ""},
            {"filename": "DASH-004-unknown.md", "content": ""},
        ]
        result = compute_sprint_summary(
            [{"story_id": f"DASH-{i:03d}"} for i in range(1, 5)],
            [],
            [],
            escalations,
            [],
        )
        assert result["escalation_breakdown"]["scope"] == 2
        assert result["escalation_breakdown"]["install"] == 1
        assert result["escalation_breakdown"]["other"] == 1

    def test_default_fields_present(self) -> None:
        result = compute_sprint_summary([], [], [], [], [])
        expected_keys = [
            "cycle_time_avg_days", "sprint_completion_pct", "stories_shipped",
            "stories_committed", "coverage_new_code_avg", "regression_rate_pct",
            "constitution_pass_pct", "escalation_rate_pct", "iteration_avg",
            "correction_rate_pct", "gate_rejection_rates", "escalation_breakdown",
            "phase_avg_hrs", "deploy_frequency", "agent_exec_hrs_avg",
            "human_wait_hrs_avg", "mutation_score_avg",
        ]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"
