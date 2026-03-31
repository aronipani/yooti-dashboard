# SSM Parameter Store entries for Lambda environment variables.
# All values are placeholders — real values set manually after apply.

locals {
  # String parameters (non-sensitive)
  string_parameters = {
    DYNAMODB_TABLE = "CHANGE_ME"
    AWS_REGION     = "us-east-1"
    CORS_ORIGINS   = "CHANGE_ME"
    LOG_LEVEL      = "INFO"
  }

  # SecureString parameters (sensitive — never commit real values)
  secure_parameters = {
    ANTHROPIC_API_KEY = "CHANGE_ME"
  }
}

resource "aws_ssm_parameter" "string" {
  for_each = local.string_parameters

  name        = "/${var.project}/${var.environment}/${each.key}"
  type        = "String"
  value       = each.value
  description = "${each.key} for ${var.project} ${var.environment}"

  tags = merge(var.tags, {
    Name = "/${var.project}/${var.environment}/${each.key}"
  })

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "secure" {
  for_each = local.secure_parameters

  name        = "/${var.project}/${var.environment}/${each.key}"
  type        = "SecureString"
  value       = each.value
  description = "${each.key} for ${var.project} ${var.environment} (set real value manually)"

  tags = merge(var.tags, {
    Name = "/${var.project}/${var.environment}/${each.key}"
  })

  lifecycle {
    ignore_changes = [value]
  }
}
