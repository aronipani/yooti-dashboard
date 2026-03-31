## DASH-015 — Terraform SSM Parameter Store module

### Acceptance criteria coverage
| AC | Status | Test |
|----|--------|------|
| AC-1 | PASS | DYNAMODB_TABLE parameter defined as String type |
| AC-2 | PASS | ANTHROPIC_API_KEY parameter defined as SecureString type |
| AC-3 | PASS | CORS_ORIGIN and AWS_REGION parameters defined as String type |
| AC-4 | PASS | All parameter values set to placeholder defaults (e.g., "CHANGE_ME") — no real secrets |
| AC-5 | PASS | infra/README.md updated with SSM parameter documentation and usage instructions |
| AC-6 | N/A | checkov scan deferred — tool not installed locally |

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
- `infra/modules/ssm/main.tf` — SSM parameters for DYNAMODB_TABLE (String), ANTHROPIC_API_KEY (SecureString), CORS_ORIGIN (String), AWS_REGION (String) with hierarchical naming /{project}/{env}/
- `infra/modules/ssm/variables.tf` — Variables for project_name, environment, parameter values, and tags
- `infra/modules/ssm/outputs.tf` — Outputs for parameter ARNs and names for use in Lambda IAM policies
- `infra/README.md` — Updated with SSM parameter reference table and post-deploy instructions

### Deliberate decisions
1. **SecureString for API keys only** — ANTHROPIC_API_KEY uses SecureString (encrypted at rest with KMS). Other parameters like DYNAMODB_TABLE and CORS_ORIGIN use plain String since they contain no sensitive data. This avoids unnecessary KMS costs.
2. **Placeholder values with lifecycle ignore** — parameters are created with "CHANGE_ME" placeholders. The lifecycle block ignores value changes so that manual updates via AWS Console or CLI are not reverted by subsequent terraform apply runs.
3. **Hierarchical naming convention** — parameters follow /{project}/{env}/{name} pattern (e.g., /yooti-dashboard/dev/DYNAMODB_TABLE) to support multiple environments and IAM path-based access policies.
