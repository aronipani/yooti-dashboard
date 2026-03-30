# Terraform Constitution
# Applies to: all .tf files, tfvars files, backend configs,
#             CI/CD workflows for terraform

## The golden rule
Infrastructure is code. Every rule that applies to application
code (no secrets, type safety, tests, peer review) applies to
Terraform. Infrastructure changes go through the same gates as
application changes.

## File structure — every module must have exactly these files

  main.tf        — resources only, no variables, no outputs
  variables.tf   — all input variables with type and description
  outputs.tf     — all output values with description
  versions.tf    — required_providers block and terraform block only

Optional:
  locals.tf      — local values only
  data.tf        — data sources only

Never put everything in one file.

## Module structure for this project

  infra/
    environments/
      dev/
        main.tf
        variables.tf
        terraform.tfvars
        backend.tf
      prod/
        main.tf
        variables.tf
        terraform.tfvars
        backend.tf
    modules/
      dynamodb/
      lambda/
      api-gateway/
      s3-cloudfront/
      ssm/
      vpc/

## Provider and version pinning — mandatory

  terraform {
    required_version = ">= 1.7.0"
    required_providers {
      aws = {
        source  = "hashicorp/aws"
        version = "~> 5.0"
      }
    }
  }

Never use version = "latest" or omit version constraints.

## State backend — mandatory

  terraform {
    backend "s3" {
      bucket         = "${project}-terraform-state-${environment}"
      key            = "${module}/terraform.tfstate"
      region         = "us-east-1"
      dynamodb_table = "${project}-terraform-locks"
      encrypt        = true
    }
  }

Never store state locally. Never commit state files.
Always add to .gitignore:
  .terraform/
  *.tfstate
  *.tfstate.backup
Commit .terraform.lock.hcl — it pins provider versions.

## Naming convention — mandatory

Pattern: {project}-{environment}-{resource}
Examples:
  yooti-dashboard-dev-lambda-ingest
  yooti-dashboard-prod-dynamodb-metrics

Use var.project and var.environment everywhere.
Never hardcode project name or environment in resource names.

## Tagging — mandatory on every resource

  default_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
    Repository  = var.repository_url
  }

Apply default_tags in the provider block.

## Variables — rules

Every variable must have:
  type        — always specified
  description — one clear sentence
  validation  — for strings with fixed valid values

Never use default = "" for required variables.
Never use type = any.

## Secrets — never in Terraform

Never put secrets in .tf or .tfvars files.
Use AWS SSM Parameter Store (SecureString):

  data "aws_ssm_parameter" "anthropic_api_key" {
    name            = "/${var.project}/${var.environment}/ANTHROPIC_API_KEY"
    with_decryption = true
  }

## IAM — least privilege mandatory

Never use AdministratorAccess or Action = ["*"].
Specify exact actions and resources on every IAM role.

## What to escalate

Write an escalation and stop if:
  - A resource requires cross-account access
  - A module dependency creates a circular reference
  - A required secret does not exist in SSM yet
  - The state bucket or lock table does not exist yet
  - Any resource would grant Action=["*"]

## Self-audit — mandatory before marking any Terraform task COMPLETE

Write results to .agent/evidence/{STORY-ID}/code-audit.md.

  SECURITY
  ☐ No hardcoded secrets, passwords, API keys, or account IDs
  ☐ No Action=["*"] without a documented comment
  ☐ No Resource=["*"] without a documented reason
  ☐ S3 buckets have block_public_access on all 4 settings
  ☐ Encryption enabled on all storage resources
  ☐ TLS enforced on all endpoints
  ☐ No sensitive values in committed tfvars files

  CODE QUALITY
  ☐ Every variable has type, description, and validation
  ☐ No type = any used anywhere
  ☐ No hardcoded region, account ID, or environment string
  ☐ All resource names use var.project and var.environment
  ☐ Every output has a description

  STRUCTURE
  ☐ main.tf contains resources only
  ☐ variables.tf contains inputs only
  ☐ outputs.tf contains outputs only
  ☐ versions.tf contains only required_providers and terraform blocks
  ☐ Environment files call modules only — no direct resources

  TAGGING
  ☐ Every resource tagged with Project, Environment, ManagedBy=terraform

  SCANNING
  ☐ checkov scan: 0 HIGH or CRITICAL findings
  ☐ terraform validate: passes
  ☐ terraform fmt -check: passes

  STATE
  ☐ No local state — backend.tf points to S3
  ☐ .terraform/ and *.tfstate in .gitignore
  ☐ .terraform.lock.hcl committed
