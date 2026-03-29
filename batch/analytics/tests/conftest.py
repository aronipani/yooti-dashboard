"""
Shared pytest fixtures for yooti-dashboard batch tests.
"""
import os
import pytest
import boto3
from moto import mock_aws


@pytest.fixture(autouse=True)
def aws_credentials():
    """Mock AWS credentials so no real AWS calls are made."""
    os.environ["AWS_ACCESS_KEY_ID"]     = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"]    = "testing"
    os.environ["AWS_SESSION_TOKEN"]     = "testing"
    os.environ["AWS_DEFAULT_REGION"]    = "us-east-1"
    os.environ["S3_BUCKET"]             = "test-bucket"


@pytest.fixture
def s3_bucket():
    """Create a mock S3 bucket for tests."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        yield s3
