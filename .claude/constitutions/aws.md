# AWS Services Constitution
# Applies to: lambda, dynamodb, s3
# The agent reads this before writing any AWS service code.

## The golden rule
Write code as if AWS services can fail at any time.
Every call can return a transient error.
Every SQS message can be delivered twice.
Every Lambda can cold-start. Design for this.

## Testing — mandatory
Never call real AWS services in unit tests.
Use moto for Python — @mock_aws on every test that touches boto3.
Use LocalStack for integration tests (docker compose up localstack -d).

    from moto import mock_aws
    import boto3

    @pytest.fixture(autouse=True)
    def aws_credentials(monkeypatch):
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
        monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    @mock_aws
    def test_something():
        # Create the fake resource inside the mock context
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        ...


## Lambda

Handler signature — always this exact shape:

    def handler(event: dict, context: Any) -> dict:
        return {"statusCode": 200, "body": json.dumps(result)}

Rules:
  No global mutable state between invocations
  boto3 clients at module level are fine — they are not state
  Log the event at DEBUG level only — never INFO (PII risk)
  All config from os.environ — never hardcoded ARNs or table names
  Missing required env var → raise ValueError at import time
  Catch all exceptions — never let one propagate uncaught from handler

## API Gateway

Event parsing — body is always a JSON string, never a dict:

    body      = json.loads(event.get("body") or "{}")
    path_id   = event["pathParameters"]["id"]
    query_val = (event.get("queryStringParameters") or {}).get("page", "1")

Status codes:
    201 — created
    400 — validation error (safe to show message)
    401 — unauthenticated
    403 — unauthorised
    404 — not found
    409 — conflict or duplicate
    500 — unexpected (NEVER expose internal detail to caller)

Error responses never include stack traces, file paths, or exception types.


## DynamoDB

Single table design — one DynamoDB table per service.
Use composite keys. Do not create separate tables per entity type.

Key patterns:
    PK: USER#<user_id>    SK: PROFILE
    PK: USER#<user_id>    SK: ORDER#<order_id>
    PK: ORDER#<order_id>  SK: METADATA

NEVER use Scan. ALWAYS Query with KeyConditionExpression:

    # WRONG
    table.scan(FilterExpression=Attr("status").eq("active"))

    # CORRECT
    table.query(
        KeyConditionExpression=Key("PK").eq(f"USER#{user_id}"),
        FilterExpression=Attr("status").eq("active"),
    )

Idempotency — use conditional writes to prevent duplicates:

    table.put_item(
        Item=item,
        ConditionExpression="attribute_not_exists(PK)",
    )

Error handling — always catch ClientError and check the code:

    from botocore.exceptions import ClientError
    try:
        table.put_item(Item=item, ConditionExpression="attribute_not_exists(PK)")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise DuplicateItemError(item["PK"])
        raise

Table name always from environment variable:
    TABLE_NAME = os.environ["TABLE_NAME"]






## Credentials and secrets (all services)

  Never hardcode AWS credentials — use IAM roles on Lambda and Fargate
  Never put secrets in environment variables — use Secrets Manager
  Never commit .env with real credentials — .env is always in .gitignore
  Cache Secrets Manager calls with @lru_cache to avoid per-invocation calls

## Local development

LocalStack runs at http://localhost:4566
Start with: docker compose up localstack -d
Create resources with: python scripts/create_local_resources.py
Invoke Lambda locally: python scripts/invoke_local.py

boto3 client pointing at LocalStack:

    import os
    client = boto3.client(
        "dynamodb",
        endpoint_url=os.environ.get("AWS_ENDPOINT_URL"),
        region_name="us-east-1",
    )

When AWS_ENDPOINT_URL is not set (staging/production) boto3 uses real AWS.
