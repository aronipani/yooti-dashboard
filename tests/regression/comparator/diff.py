#!/usr/bin/env python3
"""
Regression diff — yooti-dashboard
Compares current test results against the sprint baseline.
Exits 1 if any previously passing test is now failing.

Usage:
  python tests/regression/comparator/diff.py
  python tests/regression/comparator/diff.py --baseline sprint-9
"""
import json
import sys
import os
import argparse
from pathlib import Path


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def find_latest_baseline() -> str | None:
    baseline_dir = Path("tests/regression/baseline")
    baselines = sorted(baseline_dir.glob("*.json"), reverse=True)
    return str(baselines[0]) if baselines else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", help="Baseline name (e.g. sprint-9)")
    parser.add_argument("--current", default=".agent/evidence/current-results.json")
    args = parser.parse_args()

    # Find baseline
    if args.baseline:
        baseline_path = f"tests/regression/baseline/{args.baseline}.json"
    else:
        baseline_path = find_latest_baseline()

    if not baseline_path or not os.path.exists(baseline_path):
        print("No baseline found. Run yooti sprint:start to capture one.")
        sys.exit(0)

    # Load results
    if not os.path.exists(args.current):
        print(f"Current results not found: {args.current}")
        sys.exit(1)

    baseline = load_json(baseline_path)
    current  = load_json(args.current)

    baseline_passing = set(baseline.get("passing_tests", []))
    current_passing  = set(current.get("passing_tests", []))
    current_failing  = set(current.get("failing_tests", []))

    # Find regressions — was passing, now failing
    regressions = baseline_passing & current_failing

    # Find improvements — was failing, now passing
    improvements = current_passing - baseline_passing

    # Report
    print(f"Baseline: {baseline_path}")
    print(f"Tests before: {len(baseline_passing)}")
    print(f"Tests after:  {len(current_passing)}")
    print(f"Regressions:  {len(regressions)}")
    print(f"Improvements: {len(improvements)}")

    if improvements:
        print("\nNewly passing:")
        for t in sorted(improvements):
            print(f"  + {t}")

    if regressions:
        print("\nREGRESSIONS — these tests were passing and are now failing:")
        for t in sorted(regressions):
            print(f"  \u2717 {t}")
        print(f"\n{len(regressions)} regression(s) found. PR blocked.")
        sys.exit(1)
    else:
        print("\nNo regressions. All previously passing tests still pass.")
        sys.exit(0)


if __name__ == "__main__":
    main()
