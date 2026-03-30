#!/usr/bin/env python3
"""Aggregate .agent/ metrics and POST to the dashboard ingest endpoint.

Usage:
    python pipeline/scripts/aggregate-metrics.py [--project-dir PATH] [--sprint NUM] [--api-url URL]

Defaults:
    --project-dir  current working directory
    --api-url      YOOTI_DASHBOARD_API_URL environment variable
    --sprint       auto-detected from .agent/ data
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from lib.file_readers import (
    read_audit_logs,
    read_corrections,
    read_escalations,
    read_evidence_packages,
    read_gate_files,
)
from lib.ingest_client import post_ingest
from lib.metric_calculator import compute_sprint_summary


def detect_sprint_number(agent_dir: Path) -> int:
    """Auto-detect sprint number from .agent/ snapshot or gate files.

    Falls back to 1 if nothing is found.
    """
    snapshots_dir = agent_dir / "snapshots"
    if snapshots_dir.is_dir():
        for f in sorted(snapshots_dir.iterdir(), reverse=True):
            m = re.search(r"sprint[_-]?(\d+)", f.stem, re.IGNORECASE)
            if m:
                return int(m.group(1))
    return 1


def collect_stories(gates: list[dict[str, object]],
                    evidence: list[dict[str, object]]) -> list[dict[str, object]]:
    """Build a stories list from gates and evidence data.

    Stories with a G3 gate are COMPLETE; others are INCOMPLETE.
    """
    story_ids: set[str] = set()
    for g in gates:
        sid = g.get("story_id")
        if isinstance(sid, str):
            story_ids.add(sid)
    for e in evidence:
        sid = e.get("story_id")
        if isinstance(sid, str):
            story_ids.add(sid)

    g3_stories = {
        g["story_id"] for g in gates
        if g.get("gate") == "G3" and isinstance(g.get("story_id"), str)
    }

    stories: list[dict[str, object]] = []
    for sid in sorted(story_ids):
        stories.append({
            "story_id": sid,
            "status": "COMPLETE" if sid in g3_stories else "INCOMPLETE",
        })
    return stories


def build_payload(
    project_id: str,
    sprint_num: int,
    agent_dir: Path,
) -> dict[str, object]:
    """Read all .agent/ files and build the ingest payload."""
    gates = read_gate_files(str(agent_dir))
    evidence = read_evidence_packages(str(agent_dir))
    escalations = read_escalations(str(agent_dir))
    corrections = read_corrections(str(agent_dir))
    _logs = read_audit_logs(str(agent_dir))

    stories = collect_stories(gates, evidence)
    kpis = compute_sprint_summary(stories, gates, evidence, escalations, corrections)

    return {
        "project_id": project_id,
        "sprint_num": sprint_num,
        "stories": stories,
        **kpis,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    parser = argparse.ArgumentParser(
        description="Aggregate .agent/ metrics and POST to dashboard ingest."
    )
    parser.add_argument(
        "--project-dir",
        default=os.getcwd(),
        help="Root directory of the yooti project (default: cwd)",
    )
    parser.add_argument(
        "--sprint",
        type=int,
        default=None,
        help="Sprint number (default: auto-detect)",
    )
    parser.add_argument(
        "--api-url",
        default=None,
        help="Dashboard API URL (default: YOOTI_DASHBOARD_API_URL env var)",
    )
    args = parser.parse_args(argv)

    api_url = args.api_url or os.environ.get("YOOTI_DASHBOARD_API_URL", "")
    if not api_url:
        print("Error: --api-url or YOOTI_DASHBOARD_API_URL is required.", file=sys.stderr)
        return 1

    project_dir = Path(args.project_dir)
    agent_dir = project_dir / ".agent"

    sprint_num = args.sprint or detect_sprint_number(agent_dir)
    project_id = project_dir.name

    payload = build_payload(project_id, sprint_num, agent_dir)

    try:
        result = post_ingest(api_url, payload)
        print(f"Success: metrics ingested for sprint {sprint_num}. Response: {result}")
        return 0
    except ConnectionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
