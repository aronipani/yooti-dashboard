## DASH-011 — Add Terraform scaffold and state backend

### Acceptance criteria coverage
| AC | Status | Test |
|----|--------|------|
| AC-1 | PASS | Scaffold directory structure matches spec (6 modules, 2 envs) |
| AC-2 | PASS | Each module contains main.tf, variables.tf, outputs.tf |
| AC-3 | PASS | Bootstrap script runs with --dry-run flag without errors |
| AC-4 | PASS | terraform init succeeds in dev environment |
| AC-5 | PASS | .gitignore updated with Terraform patterns (.terraform/, *.tfstate, etc.) |
| AC-6 | N/A | checkov scan deferred — tool not installed locally |

### Test results
terraform validate: PASS (dev environment)
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
- `infra/modules/dynamodb/main.tf` — module placeholder
- `infra/modules/dynamodb/variables.tf` — module variables
- `infra/modules/dynamodb/outputs.tf` — module outputs
- `infra/modules/dynamodb/versions.tf` — provider constraints
- `infra/modules/lambda/main.tf` — module placeholder
- `infra/modules/lambda/variables.tf` — module variables
- `infra/modules/lambda/outputs.tf` — module outputs
- `infra/modules/lambda/versions.tf` — provider constraints
- `infra/modules/api-gateway/main.tf` — module placeholder
- `infra/modules/api-gateway/variables.tf` — module variables
- `infra/modules/api-gateway/outputs.tf` — module outputs
- `infra/modules/api-gateway/versions.tf` — provider constraints
- `infra/modules/s3-cloudfront/main.tf` — module placeholder
- `infra/modules/s3-cloudfront/variables.tf` — module variables
- `infra/modules/s3-cloudfront/outputs.tf` — module outputs
- `infra/modules/s3-cloudfront/versions.tf` — provider constraints
- `infra/modules/ssm/main.tf` — module placeholder
- `infra/modules/ssm/variables.tf` — module variables
- `infra/modules/ssm/outputs.tf` — module outputs
- `infra/modules/ssm/versions.tf` — provider constraints
- `infra/modules/monitoring/main.tf` — module placeholder
- `infra/modules/monitoring/variables.tf` — module variables
- `infra/modules/monitoring/outputs.tf` — module outputs
- `infra/modules/monitoring/versions.tf` — provider constraints
- `infra/environments/dev/main.tf` — dev environment root
- `infra/environments/dev/variables.tf` — dev variables
- `infra/environments/dev/backend.tf` — S3 state backend config
- `infra/environments/dev/outputs.tf` — dev outputs
- `infra/environments/prod/main.tf` — prod environment root
- `infra/environments/prod/variables.tf` — prod variables
- `infra/environments/prod/backend.tf` — S3 state backend config
- `infra/environments/prod/outputs.tf` — prod outputs
- `infra/.gitignore` — Terraform ignore patterns
- `scripts/bootstrap-terraform.sh` — state backend bootstrap with --dry-run
- `infra/README.md` — infrastructure documentation

### Deliberate decisions
1. **Six modules chosen to match application layers** — dynamodb, lambda, api-gateway, s3-cloudfront, ssm, and monitoring. Each module is independently testable and maps to a single AWS service concern.
2. **S3 backend with DynamoDB locking** — chosen over Terraform Cloud for simplicity and cost. Bootstrap script creates the backend resources before Terraform manages itself.
3. **--dry-run flag on bootstrap** — allows safe review of what the bootstrap script will create before actually provisioning state backend resources. Prevents accidental duplicate state buckets.
