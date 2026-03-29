#!/usr/bin/env python3
"""Generate PR body from evidence package. Usage: python generate-pr-body.py DASH-001"""
import json, sys, os
from datetime import datetime

story_id = sys.argv[1] if len(sys.argv) > 1 else "DASH-001"
req_path = f".agent/requirements/{story_id}-validated.json"
story = {}
if os.path.exists(req_path):
    with open(req_path) as f:
        story = json.load(f)

title = story.get("title", story_id)
acs = story.get("acceptance_criteria", [])
ac_table = "\n".join(f"| {ac['id']}: {ac['then'][:55]} | pending | pending |" for ac in acs)

body = f"""## {story_id}: {title}

### What changed
<!-- Agent: summarise implementation -->

### Acceptance Criteria
| Criteria | Status | Test |
|----------|--------|------|
{ac_table}

### Test Results
- Unit: .agent/evidence/{story_id}/test-results.json
- Coverage: .agent/evidence/{story_id}/coverage-summary.json
- Regression: .agent/evidence/{story_id}/regression-diff.json

### Known Gaps
<!-- Agent: document uncovered branches -->

---
Generated {datetime.now().strftime("%Y-%m-%d %H:%M")} by @yooti/cli
"""

os.makedirs(f".agent/evidence/{story_id}", exist_ok=True)
out = f".agent/evidence/{story_id}/pr-body.md"
with open(out, "w") as f:
    f.write(body)
print(f"PR body written: {out}")
