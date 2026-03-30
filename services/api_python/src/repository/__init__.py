"""
Repository layer for yooti-dashboard metrics.
Single-table DynamoDB design — no Scan operations permitted.
"""
from .errors import ItemNotFoundError, RepositoryError
from .metrics_repository import MetricsRepository

__all__ = ["MetricsRepository", "RepositoryError", "ItemNotFoundError"]
