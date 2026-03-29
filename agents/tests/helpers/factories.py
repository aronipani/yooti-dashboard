"""
Test factories — yooti-dashboard
Create test data with sensible defaults.

Usage:
    from tests.helpers.factories import create_user, create_property
    user = create_user(email="custom@test.com")
"""
from datetime import datetime, timezone
from uuid import uuid4


_counter = 0


def _next_id() -> str:
    global _counter
    _counter += 1
    return f"test-{_counter}"


def reset_counter() -> None:
    global _counter
    _counter = 0


def create_user(**overrides) -> dict:
    defaults = {
        "id": _next_id(),
        "email": f"user-{_counter}@test.com",
        "name": f"Test User {_counter}",
        "role": "user",
        "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
    }
    return {**defaults, **overrides}


def create_property(**overrides) -> dict:
    defaults = {
        "id": _next_id(),
        "address": f"{_counter} Test Street",
        "status": "active",
        "sqft": 1200,
        "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
    }
    return {**defaults, **overrides}
