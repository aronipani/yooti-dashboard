# DynamoDB single-table for yooti-metrics dashboard.
# Mirrors template.yaml MetricsTable resource exactly.

resource "aws_dynamodb_table" "metrics" {
  name         = "${var.project}-${var.environment}-metrics"
  billing_mode = "PAY_PER_REQUEST"

  # Key schema — PK (partition) + SK (sort)
  hash_key  = "PK"
  range_key = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "project_id"
    type = "S"
  }

  attribute {
    name = "updated_at"
    type = "S"
  }

  # GSI-1: project_id (HASH) + updated_at (RANGE), ALL projection
  global_secondary_index {
    name            = "GSI-1"
    hash_key        = "project_id"
    range_key       = "updated_at"
    projection_type = "ALL"
  }

  # TTL on the ttl attribute
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  # Point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  # Server-side encryption
  server_side_encryption {
    enabled = true
  }

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-metrics"
  })
}
