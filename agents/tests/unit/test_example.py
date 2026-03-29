"""
Example unit test — yooti-dashboard
Demonstrates the testing patterns for this project.
Delete this file once you have real tests.
"""
import pytest
from tests.helpers.factories import create_user, reset_counter


class TestCreateUser:
    """Factory produces correct defaults."""

    def setup_method(self):
        reset_counter()

    def test_creates_user_with_defaults(self):
        user = create_user()
        assert user["id"] == "test-1"
        assert user["email"] == "user-1@test.com"
        assert user["role"] == "user"

    def test_creates_user_with_overrides(self):
        user = create_user(email="admin@test.com", role="admin")
        assert user["email"] == "admin@test.com"
        assert user["role"] == "admin"

    def test_increments_id(self):
        user1 = create_user()
        user2 = create_user()
        assert user1["id"] != user2["id"]


class TestAddNumbers:
    """Basic arithmetic — replace with real tests."""

    def test_positive_numbers(self):
        assert 2 + 3 == 5

    def test_negative_numbers(self):
        assert -1 + -2 == -3

    def test_zero(self):
        assert 0 + 0 == 0
