"""Tests for file_readers module."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

from lib.file_readers import (
    read_audit_logs,
    read_corrections,
    read_escalations,
    read_evidence_packages,
    read_gate_files,
)


@pytest.fixture()
def agent_dir(tmp_path: Path) -> Path:
    """Create a realistic .agent/ directory structure."""
    # gates/
    gates = tmp_path / "gates"
    gates.mkdir()
    (gates / "DASH-001-G2-approved.md").write_text("Approved by architect")
    (gates / "DASH-001-G3-approved.md").write_text("PR merged")
    (gates / "DASH-002-G2-approved.md").write_text("Approved")
    (gates / "unrelated.txt").write_text("not a gate")

    # evidence/
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    story_dir = evidence / "DASH-001"
    story_dir.mkdir()
    (story_dir / "test-results.json").write_text(json.dumps({
        "story_id": "DASH-001",
        "unit": {"total": 10, "passed": 10, "failed": 0},
        "integration": {"total": 2, "passed": 2, "failed": 0},
    }))
    (story_dir / "coverage-summary.json").write_text(json.dumps({
        "story_id": "DASH-001",
        "overall": 85.0,
        "new_code": 92.5,
    }))

    # evidence folder with no JSON files
    empty_story = evidence / "DASH-002"
    empty_story.mkdir()

    # escalations/
    esc = tmp_path / "escalations"
    esc.mkdir()
    (esc / "DASH-002-scope.md").write_text("Need to touch extra file")

    # corrections/
    corr = tmp_path / "corrections"
    corr.mkdir()
    (corr / "DASH-001-T002-fix.md").write_text("Fix the validation logic")

    # logs/
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "DASH-001.log.json").write_text(json.dumps([
        {"event": "PHASE_START", "phase": 4},
        {"event": "QUALITY_RESULT", "result": "PASS"},
    ]))

    return tmp_path


class TestReadGateFiles:
    def test_reads_gate_files(self, agent_dir: Path) -> None:
        result = read_gate_files(str(agent_dir))
        assert len(result) == 3
        assert result[0] == {"story_id": "DASH-001", "gate": "G2", "filename": "DASH-001-G2-approved.md"}
        assert result[1] == {"story_id": "DASH-001", "gate": "G3", "filename": "DASH-001-G3-approved.md"}
        assert result[2] == {"story_id": "DASH-002", "gate": "G2", "filename": "DASH-002-G2-approved.md"}

    def test_missing_directory(self, tmp_path: Path) -> None:
        result = read_gate_files(str(tmp_path / "nonexistent"))
        assert result == []

    def test_empty_directory(self, tmp_path: Path) -> None:
        (tmp_path / "gates").mkdir()
        result = read_gate_files(str(tmp_path))
        assert result == []


class TestReadEvidencePackages:
    def test_reads_evidence(self, agent_dir: Path) -> None:
        result = read_evidence_packages(str(agent_dir))
        assert len(result) == 2

        dash001 = result[0]
        assert dash001["story_id"] == "DASH-001"
        assert dash001["test_results"]["unit"]["passed"] == 10
        assert dash001["coverage_summary"]["new_code"] == 92.5

        dash002 = result[1]
        assert dash002["story_id"] == "DASH-002"
        assert dash002["test_results"] is None
        assert dash002["coverage_summary"] is None

    def test_missing_directory(self, tmp_path: Path) -> None:
        result = read_evidence_packages(str(tmp_path / "nonexistent"))
        assert result == []

    def test_corrupt_json(self, tmp_path: Path) -> None:
        evidence = tmp_path / "evidence" / "DASH-099"
        evidence.mkdir(parents=True)
        (evidence / "test-results.json").write_text("{bad json")
        result = read_evidence_packages(str(tmp_path))
        assert len(result) == 1
        assert result[0]["test_results"] is None


class TestReadEscalations:
    def test_reads_escalations(self, agent_dir: Path) -> None:
        result = read_escalations(str(agent_dir))
        assert len(result) == 1
        assert result[0]["filename"] == "DASH-002-scope.md"
        assert "extra file" in result[0]["content"]

    def test_missing_directory(self, tmp_path: Path) -> None:
        result = read_escalations(str(tmp_path / "nonexistent"))
        assert result == []


class TestReadCorrections:
    def test_reads_corrections(self, agent_dir: Path) -> None:
        result = read_corrections(str(agent_dir))
        assert len(result) == 1
        assert result[0]["filename"] == "DASH-001-T002-fix.md"

    def test_missing_directory(self, tmp_path: Path) -> None:
        result = read_corrections(str(tmp_path / "nonexistent"))
        assert result == []


class TestReadAuditLogs:
    def test_reads_logs(self, agent_dir: Path) -> None:
        result = read_audit_logs(str(agent_dir))
        assert len(result) == 1
        assert result[0]["filename"] == "DASH-001.log.json"
        assert len(result[0]["events"]) == 2

    def test_missing_directory(self, tmp_path: Path) -> None:
        result = read_audit_logs(str(tmp_path / "nonexistent"))
        assert result == []

    def test_corrupt_json(self, tmp_path: Path) -> None:
        logs = tmp_path / "logs"
        logs.mkdir()
        (logs / "bad.log.json").write_text("not json")
        result = read_audit_logs(str(tmp_path))
        assert len(result) == 1
        assert result[0]["events"] == []
