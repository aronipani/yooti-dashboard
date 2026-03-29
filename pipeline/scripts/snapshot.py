#!/usr/bin/env python3
"""Capture regression baseline snapshot. Usage: python snapshot.py [tag]"""
import json, subprocess, sys, os
from datetime import datetime, timezone

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip()

tag = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y%m%d-%H%M%S")
snapshot = {
    "captured_at": datetime.now(timezone.utc).isoformat(),
    "tag": tag,
    "git_sha": run("git rev-parse HEAD"),
    "git_branch": run("git branch --show-current"),
    "note": "Run with real test suite output for full baseline"
}
os.makedirs(".agent/snapshots", exist_ok=True)
fname = f".agent/snapshots/{tag}.json"
with open(fname, "w") as f:
    json.dump(snapshot, f, indent=2)
print(f"Snapshot saved: {fname}")
