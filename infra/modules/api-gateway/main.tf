# API Gateway REST API with routes for yooti-dashboard.
# Mirrors template.yaml MetricsApi + route definitions exactly.
# Includes deployment and stage resources per architect annotation.

locals {
  # Route definitions matching template.yaml.
  # key = lambda function key (matches lambda module output keys)
  routes = {
    get_current_metrics = { path = "metrics/current", method = "GET" }
    get_sprint_list     = { path = "metrics/sprints", method = "GET" }
    get_sprint_detail   = { path = "metrics/sprint/{sprint_num}", method = "GET" }
    get_trends          = { path = "metrics/trends", method = "GET" }
    get_story_detail    = { path = "metrics/story/{story_id}", method = "GET" }
    ingest_metrics      = { path = "metrics/ingest", method = "POST" }
  }

  # Split paths into segments for resource creation.
  # We need: /metrics, /metrics/current, /metrics/sprints, etc.
  path_parts = toset(flatten([
    for k, v in local.routes : [
      for i in range(length(split("/", v.path))) :
      join("/", slice(split("/", v.path), 0, i + 1))
    ]
  ]))
}

# ── REST API ────────────────────────────────────────────────

resource "aws_api_gateway_rest_api" "this" {
  name        = "${var.project}-${var.environment}-api"
  description = "Yooti Dashboard metrics API — ${var.environment}"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-api"
  })
}

# ── API Resources (path segments) ───────────────────────────

resource "aws_api_gateway_resource" "paths" {
  for_each = local.path_parts

  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id = length(split("/", each.value)) == 1 ? (
    aws_api_gateway_rest_api.this.root_resource_id
    ) : (
    aws_api_gateway_resource.paths[join("/", slice(split("/", each.value), 0, length(split("/", each.value)) - 1))].id
  )
  path_part = element(split("/", each.value), length(split("/", each.value)) - 1)
}

# ── Methods + Lambda integrations ───────────────────────────

resource "aws_api_gateway_method" "routes" {
  for_each = local.routes

  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = aws_api_gateway_resource.paths[each.value.path].id
  http_method   = each.value.method
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "routes" {
  for_each = local.routes

  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.paths[each.value.path].id
  http_method             = aws_api_gateway_method.routes[each.key].http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arns[each.key]
}

# ── Lambda permissions (allow API Gateway to invoke) ────────

resource "aws_lambda_permission" "apigw" {
  for_each = local.routes

  statement_id  = "AllowAPIGatewayInvoke-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_names[each.key]
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.this.execution_arn}/*/*"
}

# ── CORS: OPTIONS method on each route resource ─────────────

resource "aws_api_gateway_method" "cors" {
  for_each = local.routes

  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = aws_api_gateway_resource.paths[each.value.path].id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "cors" {
  for_each = local.routes

  rest_api_id = aws_api_gateway_rest_api.this.id
  resource_id = aws_api_gateway_resource.paths[each.value.path].id
  http_method = aws_api_gateway_method.cors[each.key].http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "cors" {
  for_each = local.routes

  rest_api_id = aws_api_gateway_rest_api.this.id
  resource_id = aws_api_gateway_resource.paths[each.value.path].id
  http_method = aws_api_gateway_method.cors[each.key].http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "cors" {
  for_each = local.routes

  rest_api_id = aws_api_gateway_rest_api.this.id
  resource_id = aws_api_gateway_resource.paths[each.value.path].id
  http_method = aws_api_gateway_method.cors[each.key].http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Api-Key'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'${var.cors_origins}'"
  }

  depends_on = [aws_api_gateway_integration.cors]
}

# ── Deployment and stage ────────────────────────────────────

resource "aws_api_gateway_deployment" "this" {
  rest_api_id = aws_api_gateway_rest_api.this.id

  # Redeploy when any route or integration changes.
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_method.routes,
      aws_api_gateway_integration.routes,
      aws_api_gateway_method.cors,
      aws_api_gateway_integration.cors,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_integration.routes,
    aws_api_gateway_integration.cors,
  ]
}

resource "aws_api_gateway_stage" "this" {
  deployment_id = aws_api_gateway_deployment.this.id
  rest_api_id   = aws_api_gateway_rest_api.this.id
  stage_name    = var.environment

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-api-stage"
  })
}

# ── Throttling ──────────────────────────────────────────────

resource "aws_api_gateway_method_settings" "all" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  stage_name  = aws_api_gateway_stage.this.stage_name
  method_path = "*/*"

  settings {
    throttling_burst_limit = 50
    throttling_rate_limit  = 100
  }
}
