## DASH-017 — Frontend deploy script and GitHub Actions workflow

### Acceptance criteria coverage
| AC | Status | Test |
|----|--------|------|
| AC-1 | PASS | deploy-frontend.sh runs aws s3 sync and aws cloudfront create-invalidation |
| AC-2 | PASS | GitHub Actions workflow triggers on push to main with path filter for frontend/ |
| AC-3 | PASS | S3 sync includes --cache-control headers (immutable for hashed assets, no-cache for index.html) |
| AC-4 | PASS | Workflow uses aws-actions/configure-aws-credentials with OIDC role (no long-lived keys) |
| AC-5 | PASS | CloudFront invalidation of /* ensures latest build is served after deploy |

### Test results
terraform validate: N/A (shell script and YAML workflow — no Terraform)
Unit: 0/0 (infrastructure story — no unit tests)
Integration: 0/0 (infrastructure story — no integration tests)
Regression: 0 newly failing

### Coverage
N/A — Infrastructure-as-code and CI/CD configuration. No executable application code.

### Security
Snyk: 0 critical, 0 high
Semgrep: 0 findings
Checkov: not installed — manual review performed

### Files changed
- `scripts/deploy-frontend.sh` — Shell script that builds frontend, syncs to S3 with cache headers, and creates CloudFront invalidation. Accepts environment parameter (dev/prod) and reads config from terraform output.
- `.github/workflows/deploy-frontend.yml` — GitHub Actions workflow triggered on merge to main for frontend/ path changes. Uses OIDC for AWS credentials, runs npm build, and executes deploy script.

### Deliberate decisions
1. **OIDC over IAM access keys** — the workflow uses aws-actions/configure-aws-credentials with role-to-assume and OIDC federation. No AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY secrets are stored in GitHub. This is the AWS-recommended approach for GitHub Actions.
2. **Differential cache-control headers** — hashed assets (JS/CSS with content hashes in filenames) get `max-age=31536000, immutable` for aggressive caching. index.html gets `no-cache` so browsers always fetch the latest version pointing to current asset hashes.
3. **Wildcard invalidation with cost awareness** — the script invalidates /* which covers all paths. This is simpler than tracking individual changed files. The first 1000 invalidation paths per month are free on CloudFront, which is sufficient for this project's deploy frequency.
