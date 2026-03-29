"""
S3 utility — yooti-dashboard
Thin wrapper around boto3 S3 client.
Use @mock_aws from moto in all tests.
"""
import os
import boto3
import structlog
from typing import Any

log = structlog.get_logger()


class S3Client:
    def __init__(self) -> None:
        self.client = boto3.client(
            "s3",
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )
        self.bucket = os.environ.get("S3_BUCKET", "")

    def read_json(self, key: str) -> Any:
        """Read and parse a JSON file from S3."""
        import json
        log.info("s3.read", key=key)
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return json.loads(response["Body"].read())

    def write_json(self, key: str, data: Any) -> None:
        """Write a JSON file to S3."""
        import json
        log.info("s3.write", key=key)
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json",
        )
