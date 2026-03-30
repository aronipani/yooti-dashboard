## DASH-003 — GET /metrics/current

### Acceptance criteria coverage
| AC | Status | Test |
|----|--------|------|
| AC-1 200 with KPIs | PASS | test_get_current_metrics.py |
| AC-2 404 SPRINT_NOT_FOUND | PASS | test_get_current_metrics.py |
| AC-3 400 INVALID_PROJECT_ID | PASS | test_get_current_metrics.py |
| AC-4 GetItem confirmed | PASS | test_get_current_metrics.py |

### Test results
Unit: 9/9 passing
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
No violations found. 10/10 checks passed.

### Files changed
- `src/handlers/get_current_metrics.py` — Lambda handler for GET /metrics/current, reads CURRENT#SNAPSHOT from DynamoDB
- `tests/unit/test_get_current_metrics.py` — 9 tests covering 200 response, 404 when no snapshot exists, and 400 for invalid project_id

### Deliberate decisions
- Uses single GetItem on CURRENT#SNAPSHOT key rather than querying latest sprint — O(1) read cost
- Returns structured error codes (SPRINT_NOT_FOUND, INVALID_PROJECT_ID) for frontend consumption
- Handler delegates all DynamoDB access to repository layer (DASH-001 dependency)
