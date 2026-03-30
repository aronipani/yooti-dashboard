"""HTTP client for POSTing metrics to the ingest endpoint."""
from __future__ import annotations

from typing import Any

import requests


def post_ingest(
    api_url: str,
    payload: dict[str, Any],
    api_key: str = "",
) -> dict[str, Any]:
    """POST metrics payload to the ingest endpoint.

    Args:
        api_url: Base URL of the dashboard API (e.g. http://localhost:8000).
        payload: Dict matching the ingest schema.
        api_key: Optional API key for Authorization header.

    Returns:
        Parsed JSON response dict.

    Raises:
        ConnectionError: Network failure or endpoint unreachable.
        ValueError: Non-2xx HTTP response.
    """
    url = f"{api_url.rstrip('/')}/metrics/ingest"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
    except requests.exceptions.ConnectionError as exc:
        raise ConnectionError(
            f"Could not connect to ingest endpoint at {url}: {exc}"
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise ConnectionError(
            f"Request to {url} timed out: {exc}"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise ConnectionError(
            f"Request to {url} failed: {exc}"
        ) from exc

    if not resp.ok:
        raise ValueError(
            f"Ingest endpoint returned HTTP {resp.status_code}: {resp.text}"
        )

    try:
        return resp.json()  # type: ignore[no-any-return]
    except ValueError:
        return {"status": "ok", "http_status": resp.status_code}
