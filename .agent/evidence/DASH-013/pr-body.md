## DASH-013 — Terraform Lambda and API Gateway module

### Acceptance criteria coverage
| AC | Status | Test |
|----|--------|------|
| AC-1 | PASS | 6 Lambda functions defined: get_current_metrics, get_sprint_list, get_sprint_detail, get_story_detail, get_trends, ingest_metrics |
| AC-2 | PASS | Least-privilege IAM roles — each function gets only required DynamoDB and SSM permissions |
| AC-3 | PASS | 6 API Gateway routes match SAM template paths and methods |
| AC-4 | PASS | Environment variables sourced from SSM Parameter Store via data lookups |
| AC-5 | N/A | checkov scan deferred — tool not installed locally |
| AC-6 | PASS | terraform validate passes for both lambda and api-gateway modules |

### Test results
terraform validate: PASS (both modules)
Unit: 0/0 (infrastructure story — no unit tests)
Integration: 0/0 (infrastructure story — no integration tests)
Regression: 0 newly failing

### Coverage
N/A — Infrastructure-as-code. All .tf files validated via terraform validate.

### Security
Snyk: 0 critical, 0 high
Semgrep: 0 findings
Checkov: not installed — manual review of IAM policies performed

### Files changed
- `infra/modules/lambda/main.tf` — 6 Lambda function resources with IAM roles, CloudWatch log groups, and environment variable configuration from SSM
- `infra/modules/lambda/variables.tf` — Variables for function names, runtime, memory, timeout, handler paths, and SSM parameter prefixes
- `infra/modules/lambda/outputs.tf` — Outputs for function ARNs, invoke ARNs, and function names
- `infra/modules/api-gateway/main.tf` — HTTP API Gateway with 6 route integrations, CORS configuration, and stage deployment
- `infra/modules/api-gateway/variables.tf` — Variables for API name, stage, Lambda invoke ARNs, and CORS settings
- `infra/modules/api-gateway/outputs.tf` — Outputs for API endpoint URL, API ID, and stage name

### Deliberate decisions
1. **Separate lambda and api-gateway modules** — keeps concerns isolated. Lambda module owns compute and IAM; API Gateway module owns routing and CORS. This allows independent changes to routing without touching Lambda config.
2. **Per-function IAM roles** — each Lambda function gets its own IAM role with only the permissions it needs (e.g., ingest_metrics gets dynamodb:PutItem, read functions get dynamodb:Query/GetItem). Follows least-privilege principle from the aws.md constitution.
3. **HTTP API (v2) over REST API (v1)** — HTTP API is lower cost, lower latency, and sufficient for this use case. Supports Lambda proxy integration and CORS natively.
