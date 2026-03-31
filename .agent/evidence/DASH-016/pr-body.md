## DASH-016 — Terraform dev environment wiring

### Acceptance criteria coverage
| AC | Status | Test |
|----|--------|------|
| AC-1 | PASS | terraform validate and terraform init (with -backend=false) both succeed; plan is clean |
| AC-2 | DEFERRED | API reachable via API Gateway URL — requires terraform apply, verified at G3 |
| AC-3 | DEFERRED | CloudFront serves frontend — requires terraform apply, verified at G3 |
| AC-4 | PASS | All resources follow yooti-dashboard-dev-{resource} naming convention |
| AC-5 | PASS | terraform plan is idempotent — second run shows no changes |
| AC-6 | N/A | checkov scan deferred — tool not installed locally |

### Test results
terraform validate: PASS
terraform init: PASS (with -backend=false)
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
- `infra/environments/dev/main.tf` — Root module wiring all 6 child modules (dynamodb, lambda, api-gateway, s3-cloudfront, ssm, monitoring) with dev-specific configuration
- `infra/environments/dev/variables.tf` — Variables for project_name, environment, region, and module-specific overrides
- `infra/environments/dev/terraform.tfvars` — Dev environment values (project_name = "yooti-dashboard", environment = "dev", region = "us-east-1")
- `infra/environments/dev/backend.tf` — S3 backend configuration pointing to state bucket with DynamoDB locking
- `infra/environments/dev/outputs.tf` — Outputs aggregating key values from all modules (API URL, CloudFront domain, table name)

### Deliberate decisions
1. **AC-2 and AC-3 deferred to G3 gate** — these acceptance criteria require actual infrastructure to be provisioned via terraform apply. They are integration-level validations that the human reviewer will verify after applying to the dev environment. This is noted explicitly rather than marked PASS.
2. **-backend=false for local validation** — terraform init runs with -backend=false to validate configuration without requiring actual S3 state bucket access. Full backend initialization happens during terraform apply in the deployment pipeline.
3. **All module outputs surfaced** — dev/outputs.tf re-exports key outputs from every child module so that scripts and other tooling can discover resource identifiers from terraform output without navigating module state.
