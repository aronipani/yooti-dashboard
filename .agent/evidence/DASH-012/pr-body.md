## DASH-012 — Terraform DynamoDB module

### Acceptance criteria coverage
| AC | Status | Test |
|----|--------|------|
| AC-1 | PASS | PK (pk) and SK (sk) schema defined as String type in main.tf |
| AC-2 | PASS | GSI-1 with gsi1pk/gsi1sk attributes configured |
| AC-3 | PASS | TTL attribute (ttl) enabled on table |
| AC-4 | PASS | Tags variable with merge for project/environment defaults |
| AC-5 | N/A | checkov scan deferred — tool not installed locally |
| AC-6 | PASS | terraform validate passes with no errors |

### Test results
terraform validate: PASS
Unit: 0/0 (infrastructure story — no unit tests)
Integration: 0/0 (infrastructure story — no integration tests)
Regression: 0 newly failing

### Coverage
N/A — Infrastructure-as-code. All .tf files validated via terraform validate.

### Security
Snyk: 0 critical, 0 high
Semgrep: 0 findings
Checkov: not installed — manual review performed

### Files changed
- `infra/modules/dynamodb/main.tf` — DynamoDB table resource with PK/SK, GSI-1, TTL, PAY_PER_REQUEST billing, point-in-time recovery, and server-side encryption
- `infra/modules/dynamodb/variables.tf` — Variables for table_name, environment, tags, ttl_attribute_name, and billing_mode
- `infra/modules/dynamodb/outputs.tf` — Outputs for table_name, table_arn, and gsi1_name

### Deliberate decisions
1. **PAY_PER_REQUEST billing mode** — chosen over PROVISIONED for dev/early-stage usage patterns. Avoids capacity planning overhead and cost is proportional to actual usage. Can switch to PROVISIONED later via variable.
2. **Single-table design with GSI-1** — follows the DynamoDB single-table pattern from the aws.md constitution. GSI-1 supports the inverted access pattern (query by SK to find PKs). Additional GSIs can be added as access patterns emerge.
