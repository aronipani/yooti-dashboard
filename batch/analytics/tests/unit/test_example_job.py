"""
Example batch job unit test.
Shows the testing pattern — replace with real tests.
All AWS calls are mocked — no real AWS account needed.
"""
import pytest
from unittest.mock import patch
from src.jobs.example_job import run


class TestExampleJob:
    def test_returns_success_status_on_completion(self) -> None:
        result = run({})
        assert result["status"] == "success"

    def test_returns_processed_count(self) -> None:
        result = run({})
        assert "processed" in result

    def test_handles_exception_gracefully(self) -> None:
        with patch("src.jobs.example_job.log") as mock_log:
            mock_log.info.side_effect = [None, Exception("boom")]
            result = run({})
            # Should return error status not raise
            assert result["status"] in ("success", "error")


# ── Pattern reminder ──────────────────────────────────────────
# Always mock AWS services with @mock_aws from moto
# Never make real AWS calls in unit tests
# Use the s3_bucket fixture from conftest.py for S3 tests
