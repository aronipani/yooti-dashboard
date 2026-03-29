#!/usr/bin/env python3
"""
Create local AWS resources in LocalStack.
Run once after: docker compose up localstack -d

Usage:
    python scripts/create_local_resources.py
"""
import boto3
import json
import os
import sys
import time

ENDPOINT  = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566")
REGION    = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
CREDS     = {
    "endpoint_url":          ENDPOINT,
    "region_name":           REGION,
    "aws_access_key_id":     os.environ.get("AWS_ACCESS_KEY_ID", "test"),
    "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
}


def wait_for_localstack():
    import urllib.request
    for attempt in range(30):
        try:
            urllib.request.urlopen(f"{ENDPOINT}/_localstack/health", timeout=2)
            print(f"✓ LocalStack is ready at {ENDPOINT}")
            return
        except Exception:
            print(f"  Waiting for LocalStack... ({attempt + 1}/30)")
            time.sleep(2)
    print("✗ LocalStack did not start in time")
    print("  Run: docker compose up localstack -d")
    sys.exit(1)


def create_dynamodb_tables():
    client = boto3.client("dynamodb", **CREDS)
    tables = [
        {
            "TableName": "yooti-dashboard",
            "AttributeDefinitions": [
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            "KeySchema": [
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            "BillingMode": "PAY_PER_REQUEST",
        }
    ]
    for table in tables:
        try:
            client.create_table(**table)
            print(f"✓ DynamoDB table: {table['TableName']}")
        except client.exceptions.ResourceInUseException:
            print(f"~ DynamoDB table exists: {table['TableName']}")




def create_s3_buckets():
    client = boto3.client("s3", **CREDS)
    buckets = ["yooti-dashboard-data", "yooti-dashboard-firehose"]
    for bucket in buckets:
        try:
            client.create_bucket(Bucket=bucket)
            print(f"✓ S3 bucket: {bucket}")
        except Exception as e:
            if "BucketAlreadyOwnedByYou" in str(e):
                print(f"~ S3 bucket exists: {bucket}")
            else:
                raise



if __name__ == "__main__":
    print(f"Creating local AWS resources in LocalStack ({ENDPOINT})...\n")
    wait_for_localstack()
    create_dynamodb_tables()


    create_s3_buckets()

    print("\n✓ Local environment ready")
    print(f"  All services at {ENDPOINT}")
    print("\nQuick checks:")
    print("  aws dynamodb list-tables")

    print("  aws s3 ls")
