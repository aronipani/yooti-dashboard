"""Tests for ingest_client module — all HTTP calls are mocked."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from lib.ingest_client import post_ingest


SAMPLE_PAYLOAD = {
    "project_id": "test-project",
    "sprint_num": 1,
    "stories": [],
    "stories_committed": 0,
    "stories_shipped": 0,
}


class TestPostIngest:
    @patch("lib.ingest_client.requests.post")
    def test_successful_post_201(self, mock_post: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"id": "abc123", "status": "created"}
        mock_post.return_value = mock_resp

        result = post_ingest("http://localhost:8000", SAMPLE_PAYLOAD)

        assert result == {"id": "abc123", "status": "created"}
        mock_post.assert_called_once_with(
            "http://localhost:8000/metrics/ingest",
            json=SAMPLE_PAYLOAD,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

    @patch("lib.ingest_client.requests.post")
    def test_successful_post_200_idempotent(self, mock_post: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "updated"}
        mock_post.return_value = mock_resp

        result = post_ingest("http://localhost:8000", SAMPLE_PAYLOAD)
        assert result == {"status": "updated"}

    @patch("lib.ingest_client.requests.post")
    def test_api_key_sent_in_header(self, mock_post: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_resp

        post_ingest("http://localhost:8000", SAMPLE_PAYLOAD, api_key="secret")

        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["headers"]["Authorization"] == "Bearer secret"

    @patch("lib.ingest_client.requests.post")
    def test_connection_error(self, mock_post: MagicMock) -> None:
        mock_post.side_effect = requests.exceptions.ConnectionError("refused")

        with pytest.raises(ConnectionError, match="Could not connect"):
            post_ingest("http://localhost:8000", SAMPLE_PAYLOAD)

    @patch("lib.ingest_client.requests.post")
    def test_timeout_error(self, mock_post: MagicMock) -> None:
        mock_post.side_effect = requests.exceptions.Timeout("timed out")

        with pytest.raises(ConnectionError, match="timed out"):
            post_ingest("http://localhost:8000", SAMPLE_PAYLOAD)

    @patch("lib.ingest_client.requests.post")
    def test_non_2xx_raises_value_error(self, mock_post: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 422
        mock_resp.text = "Validation error"
        mock_post.return_value = mock_resp

        with pytest.raises(ValueError, match="HTTP 422"):
            post_ingest("http://localhost:8000", SAMPLE_PAYLOAD)

    @patch("lib.ingest_client.requests.post")
    def test_trailing_slash_stripped(self, mock_post: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_resp

        post_ingest("http://localhost:8000/", SAMPLE_PAYLOAD)

        call_url = mock_post.call_args.args[0] if mock_post.call_args.args else mock_post.call_args.kwargs.get("url", mock_post.call_args[0][0])
        assert call_url == "http://localhost:8000/metrics/ingest"
