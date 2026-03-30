"""Read .agent/ directory files for sprint metrics aggregation."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def read_gate_files(agent_dir: str | Path) -> list[dict[str, Any]]:
    """Scan .agent/gates/ for *-G*-approved.md files.

    Returns list of dicts with keys: story_id, gate, filename.
    Missing directory returns empty list.
    """
    gates_dir = Path(agent_dir) / "gates"
    if not gates_dir.is_dir():
        return []

    results: list[dict[str, Any]] = []
    pattern = re.compile(r"^(.+?)-(G\d+)-approved\.md$")
    for f in sorted(gates_dir.iterdir()):
        m = pattern.match(f.name)
        if m:
            results.append({
                "story_id": m.group(1),
                "gate": m.group(2),
                "filename": f.name,
            })
    return results


def read_evidence_packages(agent_dir: str | Path) -> list[dict[str, Any]]:
    """Scan .agent/evidence/ for story evidence folders.

    Each subfolder may contain test-results.json and coverage-summary.json.
    Returns list of dicts with keys: story_id, test_results, coverage_summary.
    """
    evidence_dir = Path(agent_dir) / "evidence"
    if not evidence_dir.is_dir():
        return []

    results: list[dict[str, Any]] = []
    for story_dir in sorted(evidence_dir.iterdir()):
        if not story_dir.is_dir():
            continue
        entry: dict[str, Any] = {"story_id": story_dir.name}

        tr_path = story_dir / "test-results.json"
        if tr_path.is_file():
            try:
                entry["test_results"] = json.loads(tr_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                entry["test_results"] = None
        else:
            entry["test_results"] = None

        cs_path = story_dir / "coverage-summary.json"
        if cs_path.is_file():
            try:
                entry["coverage_summary"] = json.loads(cs_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                entry["coverage_summary"] = None
        else:
            entry["coverage_summary"] = None

        results.append(entry)
    return results


def read_escalations(agent_dir: str | Path) -> list[dict[str, str]]:
    """Scan .agent/escalations/ for *.md files.

    Returns list of dicts with keys: filename, content.
    """
    esc_dir = Path(agent_dir) / "escalations"
    if not esc_dir.is_dir():
        return []

    results: list[dict[str, str]] = []
    for f in sorted(esc_dir.iterdir()):
        if f.suffix == ".md" and f.is_file():
            try:
                content = f.read_text(encoding="utf-8")
            except OSError:
                content = ""
            results.append({"filename": f.name, "content": content})
    return results


def read_corrections(agent_dir: str | Path) -> list[dict[str, str]]:
    """Scan .agent/corrections/ for *.md files.

    Returns list of dicts with keys: filename, content.
    """
    corr_dir = Path(agent_dir) / "corrections"
    if not corr_dir.is_dir():
        return []

    results: list[dict[str, str]] = []
    for f in sorted(corr_dir.iterdir()):
        if f.suffix == ".md" and f.is_file():
            try:
                content = f.read_text(encoding="utf-8")
            except OSError:
                content = ""
            results.append({"filename": f.name, "content": content})
    return results


def read_audit_logs(agent_dir: str | Path) -> list[dict[str, Any]]:
    """Scan .agent/logs/ for *.log.json files.

    Returns list of dicts with keys: filename, events (list of parsed JSON entries).
    """
    logs_dir = Path(agent_dir) / "logs"
    if not logs_dir.is_dir():
        return []

    results: list[dict[str, Any]] = []
    for f in sorted(logs_dir.iterdir()):
        if f.name.endswith(".log.json") and f.is_file():
            try:
                events = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                events = []
            results.append({"filename": f.name, "events": events})
    return results
