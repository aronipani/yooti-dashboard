## DASH-007 — aggregate-metrics.py pipeline script

### Acceptance criteria coverage
| AC | Status | Test |
|----|--------|------|
| AC-1 | PASS | test_aggregate_metrics.py — reads .agent/ files and POSTs to ingest endpoint |
| AC-2 | PASS | test_aggregate_metrics.py — missing gate marks sprint INCOMPLETE |
| AC-3 | PASS | test_aggregate_metrics.py — idempotent re-runs produce same result |
| AC-4 | PASS | test_ingest_client.py — unavailable API returns structured error |
| AC-5 | PASS | test_aggregate_metrics.py — script callable from pipeline automation |

### Test results
Unit: 37/37 passing
Integration: 0/0 passing
Regression: 0 newly failing

### Coverage
Overall: 79.5%
New code: 95.0%

### Security
Snyk: 0 critical, 0 high
Semgrep: 0 findings
Note: snyk and semgrep not installed locally — manual review performed

### Files changed
- pipeline/scripts/aggregate-metrics.py — Main pipeline script that reads .agent/ artifacts, computes metrics, and POSTs to the ingest API
- pipeline/scripts/lib/__init__.py — Package init for pipeline library modules
- pipeline/scripts/lib/file_readers.py — Reads and parses .agent/ plan files, gate files, and evidence packages
- pipeline/scripts/lib/metric_calculator.py — Computes sprint metrics (velocity, cycle time, quality scores) from parsed data
- pipeline/scripts/lib/ingest_client.py — HTTP client for POSTing computed metrics to the ingest API endpoint

### Deliberate decisions
- Split pipeline logic into lib/ modules (file_readers, metric_calculator, ingest_client) for testability and single-responsibility.
- Missing gate files cause the sprint to be marked INCOMPLETE rather than failing the script, so partial data is still captured.
- All external HTTP calls are isolated in ingest_client.py, making the rest of the pipeline pure and easy to test without mocks.
- Idempotency achieved by using PUT-style semantics — re-running with the same sprint data overwrites rather than duplicates.
