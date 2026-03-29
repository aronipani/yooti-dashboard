"""
Test mocks — yooti-dashboard
Shared mock implementations for external dependencies.

Usage:
    from tests.helpers.mocks import mock_logger, mock_db
"""
from unittest.mock import AsyncMock, MagicMock


def mock_logger() -> MagicMock:
    logger = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.bind = MagicMock(return_value=logger)
    return logger


def mock_db() -> AsyncMock:
    db = AsyncMock()
    db.execute = AsyncMock(return_value=None)
    db.fetch_one = AsyncMock(return_value=None)
    db.fetch_all = AsyncMock(return_value=[])
    return db


def mock_redis() -> MagicMock:
    store: dict[str, str] = {}
    redis = AsyncMock()
    redis.get = AsyncMock(side_effect=lambda k: store.get(k))
    redis.set = AsyncMock(side_effect=lambda k, v: store.update({k: v}))
    redis.delete = AsyncMock(side_effect=lambda k: store.pop(k, None))
    return redis


def mock_llm_response(content: str = "mock response") -> MagicMock:
    response = MagicMock()
    response.content = content
    return response
