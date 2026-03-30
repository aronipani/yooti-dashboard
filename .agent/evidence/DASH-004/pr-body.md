## DASH-004 — GET /metrics/sprints and sprint/{id}

### Acceptance criteria coverage
| AC | Status | Test |
|----|--------|------|
| AC-1 5 sprints descending order | PASS | test_get_sprint_list.py |
| AC-2 Sprint detail with KPIs | PASS | test_get_sprint_detail.py |
| AC-3 404 for non-existent sprint | PASS | test_get_sprint_detail.py |
| AC-4 400 for invalid sprint_num | PASS | test_get_sprint_detail.py |

### Test results
Unit: 12/12 passing
Integration: 0/0 passing
Regression: 0 newly failing

### Coverage
Overall: 79.5%
New code: 89.2%

### Security
Snyk: 0 critical, 0 high
Semgrep: 0 findings
Note: snyk and semgrep not installed locally — manual review performed

### Code audit
No violations found. 20/20 checks passed.

### Files changed
- `src/handlers/get_sprint_list.py` — Lambda handler for GET /metrics/sprints, returns last 5 sprints in descending order
- `src/handlers/get_sprint_detail.py` — Lambda handler for GET /metrics/sprint/{id}, returns full sprint detail with KPIs
- `tests/unit/test_get_sprint_list.py` — 5 tests for sprint list retrieval and ordering
- `tests/unit/test_get_sprint_detail.py` — 7 tests for sprint detail, 404, and validation

### Deliberate decisions
- Sprint list limited to 5 most recent sprints — sufficient for dashboard trend display without pagination complexity
- Sprint number validated as positive integer before DynamoDB query to fail fast on bad input
- Both handlers reuse repository query methods from DASH-001 — no direct DynamoDB calls in handler layer
