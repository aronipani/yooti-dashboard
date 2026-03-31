# Lambda functions and IAM roles for yooti-dashboard API.
# Mirrors template.yaml Lambda definitions exactly.

locals {
  runtime      = "python3.12"
  architecture = "arm64"

  # Function definitions matching template.yaml handlers and permissions.
  # read_only = true  → dynamodb:GetItem, dynamodb:Query
  # read_only = false → dynamodb:GetItem, dynamodb:Query, dynamodb:PutItem, dynamodb:BatchWriteItem
  functions = {
    get_current_metrics = {
      handler   = "src.handlers.get_current_metrics.handler"
      read_only = true
    }
    get_sprint_list = {
      handler   = "src.handlers.get_sprint_list.handler"
      read_only = true
    }
    get_sprint_detail = {
      handler   = "src.handlers.get_sprint_detail.handler"
      read_only = true
    }
    get_trends = {
      handler   = "src.handlers.get_trends.handler"
      read_only = true
    }
    get_story_detail = {
      handler   = "src.handlers.get_story_detail.handler"
      read_only = true
    }
    ingest_metrics = {
      handler   = "src.handlers.ingest_metrics.handler"
      read_only = false
    }
  }
}

# ── Package source code as zip ──────────────────────────────

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = var.source_code_path
  output_path = "${path.module}/.build/lambda.zip"

  excludes = [
    "tests",
    "tests/**",
    "__pycache__",
    "**/__pycache__",
    ".coverage",
    "coverage.json",
    ".gitignore",
    "Dockerfile",
    ".dockerignore",
  ]
}

# ── IAM: assume role policy (shared) ────────────────────────

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# ── IAM: DynamoDB read-only policy ──────────────────────────

data "aws_iam_policy_document" "dynamodb_read" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:Query",
    ]
    resources = [
      var.dynamodb_table_arn,
      var.gsi_arn,
    ]
  }
}

# ── IAM: DynamoDB read-write policy (ingest) ────────────────

data "aws_iam_policy_document" "dynamodb_read_write" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:Query",
      "dynamodb:PutItem",
      "dynamodb:BatchWriteItem",
    ]
    resources = [
      var.dynamodb_table_arn,
      var.gsi_arn,
    ]
  }
}

# ── IAM: CloudWatch Logs policy (shared) ────────────────────

data "aws_iam_policy_document" "cloudwatch_logs" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

# ── Per-function resources ──────────────────────────────────

resource "aws_iam_role" "lambda" {
  for_each = local.functions

  name               = "${var.project}-${var.environment}-${replace(each.key, "_", "-")}-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-${replace(each.key, "_", "-")}-role"
  })
}

resource "aws_iam_role_policy" "dynamodb" {
  for_each = local.functions

  name   = "dynamodb-access"
  role   = aws_iam_role.lambda[each.key].id
  policy = each.value.read_only ? data.aws_iam_policy_document.dynamodb_read.json : data.aws_iam_policy_document.dynamodb_read_write.json
}

resource "aws_iam_role_policy" "cloudwatch" {
  for_each = local.functions

  name   = "cloudwatch-logs"
  role   = aws_iam_role.lambda[each.key].id
  policy = data.aws_iam_policy_document.cloudwatch_logs.json
}

resource "aws_lambda_function" "this" {
  for_each = local.functions

  function_name = "${var.project}-${var.environment}-${replace(each.key, "_", "-")}"
  role          = aws_iam_role.lambda[each.key].arn
  handler       = each.value.handler
  runtime       = local.runtime
  architectures = [local.architecture]
  memory_size   = var.memory_size
  timeout       = var.timeout

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = var.dynamodb_table_name
      LOG_LEVEL  = "INFO"
    }
  }

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-${replace(each.key, "_", "-")}"
  })
}
