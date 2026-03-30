"""
Unit tests for DynamoDB key builders.
Tests that all PK/SK patterns match ARCH-DASHBOARD.md Section 3.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.repository.keys import (
    pk,
    sk_sprint_summary,
    sk_story,
    sk_phase,
    sk_trend,
    sk_current_snapshot,
    sk_gate,
    sk_escalation,
    sk_sprint_prefix,
    sk_story_prefix,
    sk_trend_metric_prefix,
    sk_gate_prefix,
    sk_esc_prefix,
)


class TestPartitionKey:
    def test_builds_project_prefixed_key(self) -> None:
        assert pk("yooti-ri") == "PROJECT#yooti-ri"

    def test_handles_different_project_ids(self) -> None:
        assert pk("my-project") == "PROJECT#my-project"


class TestSprintSummarySortKey:
    def test_builds_sprint_summary_key(self) -> None:
        assert sk_sprint_summary(10) == "SPRINT#10#SUMMARY"

    def test_sprint_num_zero(self) -> None:
        assert sk_sprint_summary(0) == "SPRINT#0#SUMMARY"


class TestStorySortKey:
    def test_builds_story_key(self) -> None:
        assert sk_story(10, "PROJ-123") == "SPRINT#10#STORY#PROJ-123"


class TestPhaseSortKey:
    def test_builds_phase_key(self) -> None:
        assert sk_phase(10, "PROJ-123") == "SPRINT#10#PHASE#PROJ-123"


class TestTrendSortKey:
    def test_builds_trend_key(self) -> None:
        assert sk_trend("cycle_time_avg", 10) == "TREND#cycle_time_avg#SPRINT#10"


class TestCurrentSnapshotSortKey:
    def test_returns_fixed_key(self) -> None:
        assert sk_current_snapshot() == "CURRENT#SNAPSHOT"


class TestGateSortKey:
    def test_builds_gate_key(self) -> None:
        assert sk_gate("PROJ-123", 3) == "GATE#PROJ-123#G3"


class TestEscalationSortKey:
    def test_builds_escalation_key(self) -> None:
        assert sk_escalation("PROJ-123", "T001") == "ESC#PROJ-123#T001"


class TestPrefixes:
    def test_sprint_prefix(self) -> None:
        assert sk_sprint_prefix(10) == "SPRINT#10#"

    def test_story_prefix(self) -> None:
        assert sk_story_prefix(10) == "SPRINT#10#STORY#"

    def test_trend_metric_prefix(self) -> None:
        assert sk_trend_metric_prefix("cycle_time_avg") == "TREND#cycle_time_avg#"

    def test_gate_prefix(self) -> None:
        assert sk_gate_prefix("PROJ-123") == "GATE#PROJ-123#"

    def test_esc_prefix(self) -> None:
        assert sk_esc_prefix("PROJ-123") == "ESC#PROJ-123#"
