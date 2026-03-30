"""
Unit tests for repository error types.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.repository.errors import (
    ItemNotFoundError,
    RepositoryError,
)


class TestRepositoryError:
    def test_stores_message(self) -> None:
        err = RepositoryError("something failed")
        assert err.message == "something failed"
        assert str(err) == "something failed"

    def test_is_exception(self) -> None:
        err = RepositoryError("fail")
        assert isinstance(err, Exception)


class TestItemNotFoundError:
    def test_is_repository_error(self) -> None:
        err = ItemNotFoundError("Sprint", "10")
        assert isinstance(err, RepositoryError)

    def test_stores_entity_and_key(self) -> None:
        err = ItemNotFoundError("Sprint", "10")
        assert err.entity == "Sprint"
        assert err.key == "10"

    def test_message_includes_entity_and_key(self) -> None:
        err = ItemNotFoundError("Sprint", "10")
        assert "Sprint" in str(err)
        assert "10" in str(err)
