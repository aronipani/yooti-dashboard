#!/usr/bin/env bash
#
# deploy-frontend.sh — builds the React frontend and deploys to S3 + CloudFront.
#
# Required environment variables:
#   S3_BUCKET              — S3 bucket name (from Terraform output)
#   CF_DISTRIBUTION_ID     — CloudFront distribution ID (from Terraform output)
#
# Usage:
#   S3_BUCKET=yooti-dashboard-dev-frontend \
#   CF_DISTRIBUTION_ID=E1234567890 \
#   ./scripts/deploy-frontend.sh
#
set -euo pipefail

# ── Validate required env vars ──────────────────────────────

if [ -z "${S3_BUCKET:-}" ]; then
  echo "ERROR: S3_BUCKET environment variable is required."
  echo "Get it from: cd infra/environments/dev && terraform output s3_bucket_name"
  exit 1
fi

if [ -z "${CF_DISTRIBUTION_ID:-}" ]; then
  echo "ERROR: CF_DISTRIBUTION_ID environment variable is required."
  echo "Get it from: cd infra/environments/dev && terraform output cloudfront_distribution_id"
  exit 1
fi

FRONTEND_DIR="frontend/dashboard"

echo "=== Deploy Frontend ==="
echo "Bucket:       ${S3_BUCKET}"
echo "Distribution: ${CF_DISTRIBUTION_ID}"
echo ""

# ── Build ───────────────────────────────────────────────────

echo "--- Building frontend ---"
cd "${FRONTEND_DIR}"
npm ci --silent
npm run build
cd - > /dev/null

echo ""

# ── Sync hashed assets (long cache) ────────────────────────

echo "--- Syncing hashed assets (max-age=31536000) ---"
aws s3 sync "${FRONTEND_DIR}/dist/assets/" "s3://${S3_BUCKET}/assets/" \
  --delete \
  --cache-control "public, max-age=31536000, immutable"

# ── Sync index.html and other root files (no cache) ────────

echo "--- Syncing root files (no-cache) ---"
aws s3 sync "${FRONTEND_DIR}/dist/" "s3://${S3_BUCKET}/" \
  --delete \
  --exclude "assets/*" \
  --cache-control "no-cache, no-store, must-revalidate"

echo ""

# ── Invalidate CloudFront cache ─────────────────────────────

echo "--- Invalidating CloudFront cache ---"
INVALIDATION_ID=$(aws cloudfront create-invalidation \
  --distribution-id "${CF_DISTRIBUTION_ID}" \
  --paths "/*" \
  --query 'Invalidation.Id' \
  --output text)

echo "Invalidation created: ${INVALIDATION_ID}"
echo ""
echo "=== Deploy complete ==="
