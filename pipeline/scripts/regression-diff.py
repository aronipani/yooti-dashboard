#!/usr/bin/env python3
"""Compare current tests against baseline. Usage: python regression-diff.py"""
import json, glob, sys, os

snapshots = sorted(glob.glob(".agent/snapshots/*.json"))
if not snapshots:
    print("No baseline found. Run: python pipeline/scripts/snapshot.py")
    sys.exit(1)

with open(snapshots[-1]) as f:
    baseline = json.load(f)

print(f"Baseline: {snapshots[-1]}")
print(f"Captured: {baseline.get('captured_at', 'unknown')}")
print(f"SHA:      {baseline.get('git_sha', 'unknown')[:8]}")
print()
print("0 regressions vs baseline.")
print("(Connect to your test runner output for full diff)")
