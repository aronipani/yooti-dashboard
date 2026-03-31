# Infrastructure — Terraform

Terraform modules and environment configurations for the Yooti Dashboard.

## Folder Structure

```
infra/
  bootstrap/                  # One-time state backend setup
    create-state-backend.sh
  modules/                    # Reusable Terraform modules
    dynamodb/                 # DynamoDB metrics table (DASH-012)
    lambda/                   # Lambda functions + IAM (DASH-013)
    api-gateway/              # REST API + routes (DASH-013)
    s3-cloudfront/            # Frontend hosting (DASH-014)
    ssm/                      # Parameter Store entries (DASH-015)
    vpc/                      # Reserved for future use
  environments/               # Per-environment wiring
    dev/                      # Development (DASH-016)
    prod/                     # Production
```

## Prerequisites

- Terraform >= 1.7.0
- AWS CLI configured with credentials
- S3 state bucket and DynamoDB lock table (created by bootstrap script)

## First-Time Setup

### 1. Create the state backend

```bash
cd infra/bootstrap
./create-state-backend.sh --environment dev
```

Or preview without creating:

```bash
./create-state-backend.sh --environment dev --dry-run
```

### 2. Initialize Terraform

```bash
cd infra/environments/dev
terraform init
```

### 3. Plan and apply

```bash
terraform plan
terraform apply
```

## Naming Convention

All resources follow: `{project}-{environment}-{resource}`

Examples:
- `yooti-dashboard-dev-metrics` (DynamoDB table)
- `yooti-dashboard-dev-lambda-ingest` (Lambda function)
- `yooti-dashboard-dev-frontend` (S3 bucket)

## Tagging

Every resource is tagged via the provider `default_tags`:

| Tag | Value |
|-----|-------|
| Project | yooti-dashboard |
| Environment | dev / prod |
| ManagedBy | terraform |

## State Management

- State stored in S3: `yooti-dashboard-terraform-state-{env}`
- Locks in DynamoDB: `yooti-dashboard-terraform-locks`
- State files are encrypted at rest
- Never commit `.terraform/` or `*.tfstate` files

## Setting SSM Parameters

After `terraform apply`, set real values for SSM parameters:

```bash
# DynamoDB table name (set automatically by Terraform outputs)
aws ssm put-parameter \
  --name "/yooti-dashboard/dev/DYNAMODB_TABLE" \
  --type String \
  --value "yooti-dashboard-dev-metrics" \
  --overwrite

# API key (must be set manually — never in Terraform)
aws ssm put-parameter \
  --name "/yooti-dashboard/dev/ANTHROPIC_API_KEY" \
  --type SecureString \
  --value "sk-ant-your-real-key-here" \
  --overwrite

# CORS origins
aws ssm put-parameter \
  --name "/yooti-dashboard/dev/CORS_ORIGINS" \
  --type String \
  --value "https://your-cloudfront-domain.cloudfront.net" \
  --overwrite
```

## Module Dependencies

```
dynamodb ──┐
ssm ───────┤
           ├── lambda ── api-gateway
s3-cloudfront (independent)
```
