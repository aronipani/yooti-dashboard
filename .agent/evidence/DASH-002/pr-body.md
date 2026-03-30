## DASH-002 — POST /metrics/ingest

### Acceptance criteria coverage
| AC | Status | Test |
|----|--------|------|
| AC-1 Valid payload returns 201 | PASS | test_ingest_metrics.py |
| AC-2 Re-ingest same sprint returns 200 | PASS | test_ingest_metrics.py |
| AC-3 Missing project_id returns 400 | PASS | test_ingest_metrics.py |
| AC-4 DynamoDB down returns 500 | PASS | test_ingest_metrics.py |
| AC-5 CURRENT#SNAPSHOT updated on ingest | PASS | test_ingest_metrics.py, test_insight_engine.py |

### Test results
Unit: 28/28 passing
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
No violations found. 60/60 checks passed.

### Files changed
- `src/handlers/__init__.py` — handlers module init
- `src/handlers/ingest_metrics.py` — Lambda handler for POST /metrics/ingest, validates and persists sprint data
- `src/validators/__init__.py` — validators module init
- `src/validators/ingest_validator.py` — request body validation for ingest payloads
- `src/services/__init__.py` — services module init
- `src/services/insight_engine.py` — computes derived KPIs and updates CURRENT#SNAPSHOT
- `tests/unit/test_ingest_metrics.py` — 12 tests covering happy path, idempotency, validation errors, and DynamoDB failures
- `tests/unit/test_insight_engine.py` — 16 tests for insight computation logic

### Deliberate decisions
- Validation layer separated from handler to keep handler thin (greenfield pattern mandate)
- Insight engine runs synchronously within the ingest handler to keep CURRENT#SNAPSHOT always consistent
- 201 for new ingestion, 200 for idempotent re-ingestion — distinguishes create vs no-op
- All DynamoDB errors wrapped in RepositoryError and surfaced as 500 with safe error message
