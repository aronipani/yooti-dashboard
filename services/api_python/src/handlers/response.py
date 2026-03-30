"""
Shared response builders for Lambda handlers.
Standard error shape from ARCH-DASHBOARD.md Section 5.
CORS headers on every response.
"""
import json
from decimal import Decimal
from typing import Any


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Api-Key",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Content-Type": "application/json",
}


class _DecimalEncoder(json.JSONEncoder):
    """Encode Decimal values as float for JSON serialization."""

    def default(self, o: object) -> Any:
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


def success(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    """Build a success response with CORS headers."""
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body, cls=_DecimalEncoder),
    }


def error(status_code: int, error_code: str, message: str) -> dict[str, Any]:
    """Build a standard error response — never exposes internal detail."""
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps({
            "error": error_code,
            "message": message,
            "statusCode": status_code,
        }),
    }
