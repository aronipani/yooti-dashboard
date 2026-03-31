# Dev environment — wires all modules together.
# DASH-016-T001

terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# ── DynamoDB ────────────────────────────────────────────────

module "dynamodb" {
  source = "../../modules/dynamodb"

  project     = var.project
  environment = var.environment
}

# ── SSM Parameter Store ─────────────────────────────────────

module "ssm" {
  source = "../../modules/ssm"

  project     = var.project
  environment = var.environment
}

# ── Lambda Functions ────────────────────────────────────────

module "lambda" {
  source = "../../modules/lambda"

  project             = var.project
  environment         = var.environment
  memory_size         = 128 # Dev cost optimization (prod uses 256)
  dynamodb_table_name = module.dynamodb.table_name
  dynamodb_table_arn  = module.dynamodb.table_arn
  gsi_arn             = module.dynamodb.gsi_1_arn
  source_code_path    = "${path.module}/../../../services/api_python"

  depends_on = [module.dynamodb]
}

# ── API Gateway ─────────────────────────────────────────────

module "api_gateway" {
  source = "../../modules/api-gateway"

  project              = var.project
  environment          = var.environment
  lambda_invoke_arns   = module.lambda.invoke_arns
  lambda_function_names = module.lambda.function_names
  cors_origins         = "http://localhost:5173"

  depends_on = [module.lambda]
}

# ── Frontend (S3 + CloudFront) ──────────────────────────────

module "frontend" {
  source = "../../modules/s3-cloudfront"

  project     = var.project
  environment = var.environment
}

# VPC module intentionally not wired — reserved for future use.
# See infra/modules/vpc/ for the skeleton.
