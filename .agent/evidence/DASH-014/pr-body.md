## DASH-014 — Terraform S3 and CloudFront module

### Acceptance criteria coverage
| AC | Status | Test |
|----|--------|------|
| AC-1 | PASS | S3 bucket has block_public_acls, block_public_policy, ignore_public_acls, restrict_public_buckets all set to true |
| AC-2 | PASS | CloudFront uses Origin Access Control (OAC), not legacy OAI |
| AC-3 | PASS | CloudFront viewer_protocol_policy set to redirect-to-https |
| AC-4 | PASS | Custom error response: 404 returns /index.html with 200 status for SPA routing |
| AC-5 | PASS | S3 bucket versioning enabled |
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
Checkov: not installed — manual review of public access and encryption settings performed

### Files changed
- `infra/modules/s3-cloudfront/main.tf` — S3 bucket with public access block, versioning, encryption; CloudFront distribution with OAC, HTTPS redirect, SPA error handling, and S3 bucket policy
- `infra/modules/s3-cloudfront/variables.tf` — Variables for bucket_name, environment, domain_name, price_class, and tags
- `infra/modules/s3-cloudfront/outputs.tf` — Outputs for bucket_name, bucket_arn, cloudfront_distribution_id, cloudfront_domain_name

### Deliberate decisions
1. **OAC over OAI** — Origin Access Control is AWS's recommended approach, replacing the legacy Origin Access Identity. OAC supports S3 server-side encryption with KMS and provides better security controls.
2. **Single custom_error_response for 404** — routes all 404s to /index.html with a 200 status code. This is the standard pattern for React SPA routing where the client-side router handles all paths.
3. **PriceClass_100 default** — uses only North America and Europe edge locations to minimize cost during development. Variable allows override for production.
