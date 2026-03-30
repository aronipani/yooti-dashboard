"""Tests for aggregate-metrics.py CLI entry point — all externals mocked."""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# Import the module with a hyphen in its name
def _import_aggregate_metrics():  # type: ignore[no-untyped-def]
    """Import aggregate-metrics.py which has a hyphen in the filename."""
    spec = importlib.util.spec_from_file_location(
        "aggregate_metrics",
        Path(__file__).resolve().parent.parent / "aggregate-metrics.py",
    )
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


aggregate_metrics = _import_aggregate_metrics()


class TestDetectSprintNumber:
    def test_detects_from_snapshot(self, tmp_path: Path) -> None:
        snapshots = tmp_path / "snapshots"
        snapshots.mkdir()
        (snapshots / "sprint-3.json").write_text("{}")
        result = aggregate_metrics.detect_sprint_number(tmp_path)
        assert result == 3

    def test_defaults_to_1(self, tmp_path: Path) -> None:
        result = aggregate_metrics.detect_sprint_number(tmp_path)
        assert result == 1


class TestCollectStories:
    def test_complete_and_incomplete(self) -> None:
        gates = [
            {"story_id": "DASH-001", "gate": "G2"},
            {"story_id": "DASH-001", "gate": "G3"},
            {"story_id": "DASH-002", "gate": "G2"},
        ]
        evidence = [
            {"story_id": "DASH-001"},
            {"story_id": "DASH-002"},
        ]
        stories = aggregate_metrics.collect_stories(gates, evidence)
        assert len(stories) == 2
        assert stories[0] == {"story_id": "DASH-001", "status": "COMPLETE"}
        assert stories[1] == {"story_id": "DASH-002", "status": "INCOMPLETE"}

    def test_missing_gate_file_incomplete(self) -> None:
        """AC-2: missing gate file means story is INCOMPLETE."""
        gates = []
        evidence = [{"story_id": "DASH-005"}]
        stories = aggregate_metrics.collect_stories(gates, evidence)
        assert stories[0]["status"] == "INCOMPLETE"


class TestBuildPayload:
    def test_builds_valid_payload(self, tmp_path: Path) -> None:
        # Setup minimal .agent/ structure
        gates = tmp_path / "gates"
        gates.mkdir()
        (gates / "DASH-001-G3-approved.md").write_text("merged")

        evidence = tmp_path / "evidence" / "DASH-001"
        evidence.mkdir(parents=True)
        (evidence / "test-results.json").write_text(json.dumps({
            "story_id": "DASH-001",
            "unit": {"total": 5, "passed": 5, "failed": 0},
            "integration": {"total": 1, "passed": 1, "failed": 0},
        }))
        (evidence / "coverage-summary.json").write_text(json.dumps({
            "story_id": "DASH-001",
            "overall": 88.0,
            "new_code": 95.0,
        }))

        payload = aggregate_metrics.build_payload("test-proj", 1, tmp_path)

        assert payload["project_id"] == "test-proj"
        assert payload["sprint_num"] == 1
        assert len(payload["stories"]) == 1
        assert payload["stories"][0]["status"] == "COMPLETE"
        assert "stories_committed" in payload
        assert "coverage_new_code_avg" in payload


class TestMain:
    @patch.object(aggregate_metrics, "post_ingest")
    def test_success_exit_0(self, mock_ingest: MagicMock, tmp_path: Path) -> None:
        """AC-1: reads .agent/ files, builds payload, POST returns 201."""
        # Create minimal .agent/ structure
        agent = tmp_path / ".agent" / "gates"
        agent.mkdir(parents=True)
        (agent / "DASH-001-G3-approved.md").write_text("ok")

        mock_ingest.return_value = {"status": "created"}

        exit_code = aggregate_metrics.main([
            "--project-dir", str(tmp_path),
            "--sprint", "1",
            "--api-url", "http://localhost:8000",
        ])

        assert exit_code == 0
        mock_ingest.assert_called_once()
        call_payload = mock_ingest.call_args[0][1]
        assert call_payload["sprint_num"] == 1

    @patch.object(aggregate_metrics, "post_ingest")
    def test_connection_error_exit_1(self, mock_ingest: MagicMock, tmp_path: Path) -> None:
        """AC-4: endpoint unavailable returns exit code 1."""
        (tmp_path / ".agent").mkdir()

        mock_ingest.side_effect = ConnectionError("Connection refused")

        exit_code = aggregate_metrics.main([
            "--project-dir", str(tmp_path),
            "--sprint", "1",
            "--api-url", "http://localhost:8000",
        ])

        assert exit_code == 1

    @patch.object(aggregate_metrics, "post_ingest")
    def test_value_error_exit_1(self, mock_ingest: MagicMock, tmp_path: Path) -> None:
        (tmp_path / ".agent").mkdir()

        mock_ingest.side_effect = ValueError("HTTP 500")

        exit_code = aggregate_metrics.main([
            "--project-dir", str(tmp_path),
            "--sprint", "1",
            "--api-url", "http://localhost:8000",
        ])

        assert exit_code == 1

    def test_missing_api_url_exit_1(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("YOOTI_DASHBOARD_API_URL", raising=False)

        exit_code = aggregate_metrics.main([
            "--project-dir", str(tmp_path),
        ])

        assert exit_code == 1

    @patch.object(aggregate_metrics, "post_ingest")
    def test_api_url_from_env(self, mock_ingest: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        (tmp_path / ".agent").mkdir()
        monkeypatch.setenv("YOOTI_DASHBOARD_API_URL", "http://env-url:8000")
        mock_ingest.return_value = {"status": "ok"}

        exit_code = aggregate_metrics.main([
            "--project-dir", str(tmp_path),
            "--sprint", "1",
        ])

        assert exit_code == 0
        assert mock_ingest.call_args[0][0] == "http://env-url:8000"

    @patch.object(aggregate_metrics, "post_ingest")
    def test_idempotent_second_run(self, mock_ingest: MagicMock, tmp_path: Path) -> None:
        """AC-3: second run returns 200 (idempotent)."""
        (tmp_path / ".agent").mkdir()
        mock_ingest.return_value = {"status": "updated"}

        exit_code = aggregate_metrics.main([
            "--project-dir", str(tmp_path),
            "--sprint", "1",
            "--api-url", "http://localhost:8000",
        ])

        assert exit_code == 0
