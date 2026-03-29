# AWS Development Guide — yooti-dashboard

Region: us-east-1
Services: lambda, dynamodb, s3
Deploy: sam

---

## Quick start

    # 1. Start LocalStack
    docker compose up localstack -d

    # 2. Create local resources (DynamoDB tables, SQS queues, etc.)
    python scripts/create_local_resources.py

    # 3. Run a Lambda handler locally
    python scripts/invoke_local.py

    # 4. Run unit tests (uses moto — no LocalStack needed)
    pytest tests/unit/

    # 5. Run integration tests (uses LocalStack)
    pytest tests/integration/

---

## Environment setup

Copy the AWS environment file:

    cp .env.aws.example .env

This sets `AWS_ENDPOINT_URL=http://localhost:4566` which redirects
all boto3 calls to LocalStack. Remove that line for staging/production.

---

## Testing strategy

| Layer | Tool | AWS calls? | When |
|-------|------|-----------|------|
| Unit tests | moto (@mock_aws) | No — fully mocked | Every commit |
| Integration | LocalStack | Yes — local emulation | Every PR |
| Staging | Real AWS | Yes — real services | After G4 |
| Production | Real AWS | Yes — real services | After G5 |

Unit tests must NEVER call real AWS or LocalStack.
Use the `@mock_aws` decorator from moto for every test.

---

## Resource names

| Resource | Local name | Staging/Prod pattern |
|----------|-----------|---------------------|
| DynamoDB table | yooti-dashboard | yooti-dashboard-{env} |
| S3 bucket | yooti-dashboard-data | yooti-dashboard-data-{env} |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/create_local_resources.py` | Create DynamoDB tables, SQS queues, etc. in LocalStack |
| `scripts/invoke_local.py` | Invoke a Lambda handler locally against LocalStack |

---

## Test events

Test event files in `events/` match API Gateway and SQS formats:

| File | Description |
|------|-------------|
| `events/api_post_valid.json` | Valid POST request |
| `events/api_post_invalid.json` | Invalid POST (empty body) |
| `events/api_get_by_id.json` | GET with path parameter |

Use with invoke script:

    python scripts/invoke_local.py --event events/api_post_valid.json

---

## SAM deployment

The `template.yaml` at the project root defines all Lambda functions
and AWS resources.

    # Validate template
    sam validate

    # Build
    sam build

    # Deploy to dev
    sam deploy --stack-name yooti-dashboard-dev --parameter-overrides Environment=dev

    # Deploy to staging
    sam deploy --stack-name yooti-dashboard-staging --parameter-overrides Environment=staging

    # Local API (uses Docker)
    sam local start-api --env-vars .env

---

## Constitution rules (summary)

The full rules are in `.claude/constitutions/aws.md`. Key points:

- **Testing**: moto for unit tests, LocalStack for integration
- **DynamoDB**: Single table design, no Scan, conditional writes for idempotency
- **SQS**: Return batchItemFailures, never fail whole batch, always have DLQ
- **Lambda**: All config from os.environ, catch all exceptions, no global mutable state
- **Credentials**: IAM roles in production, Secrets Manager for secrets, never hardcode
