#!/usr/bin/env bash
#
# create-state-backend.sh — creates the S3 bucket and DynamoDB lock table
# needed for Terraform remote state.
#
# Usage:
#   ./create-state-backend.sh                     # creates resources
#   ./create-state-backend.sh --dry-run            # prints commands only
#   ./create-state-backend.sh --environment prod   # override environment
#
set -euo pipefail

PROJECT="yooti-dashboard"
ENVIRONMENT="${ENVIRONMENT:-dev}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --environment)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

BUCKET_NAME="${PROJECT}-terraform-state-${ENVIRONMENT}"
LOCK_TABLE="${PROJECT}-terraform-locks"

run_cmd() {
  if [ "$DRY_RUN" = true ]; then
    echo "[DRY RUN] $*"
  else
    echo "[RUN] $*"
    "$@"
  fi
}

echo "=== Terraform State Backend Setup ==="
echo "Project:     ${PROJECT}"
echo "Environment: ${ENVIRONMENT}"
echo "Region:      ${REGION}"
echo "S3 Bucket:   ${BUCKET_NAME}"
echo "Lock Table:  ${LOCK_TABLE}"
echo ""

# Create S3 bucket
echo "--- Creating S3 state bucket ---"
run_cmd aws s3api create-bucket \
  --bucket "${BUCKET_NAME}" \
  --region "${REGION}"

# Enable versioning
run_cmd aws s3api put-bucket-versioning \
  --bucket "${BUCKET_NAME}" \
  --versioning-configuration Status=Enabled

# Enable server-side encryption
run_cmd aws s3api put-bucket-encryption \
  --bucket "${BUCKET_NAME}" \
  --server-side-encryption-configuration '{
    "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
  }'

# Block all public access
run_cmd aws s3api put-public-access-block \
  --bucket "${BUCKET_NAME}" \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo ""

# Create DynamoDB lock table
echo "--- Creating DynamoDB lock table ---"
run_cmd aws dynamodb create-table \
  --table-name "${LOCK_TABLE}" \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region "${REGION}"

echo ""
echo "=== Done ==="
if [ "$DRY_RUN" = true ]; then
  echo "(Dry run — no resources were created)"
else
  echo "State backend ready. You can now run:"
  echo "  cd infra/environments/${ENVIRONMENT}"
  echo "  terraform init"
fi
