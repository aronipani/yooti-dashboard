"""
Test data factories for yooti-dashboard API tests.
Add a factory for every domain model as stories are completed.
"""
from datetime import datetime
import uuid


def create_user(**overrides):
    """Create a test user dict with sensible defaults."""
    return {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "name": "Test User",
        "created_at": datetime.now().isoformat(),
        **overrides,
    }


# Add more factories here as domain models are created
