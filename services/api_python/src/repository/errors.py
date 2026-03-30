"""
Repository error types for yooti-dashboard.
All DynamoDB errors are caught and wrapped in these types.
Internal AWS details are never exposed to callers.
"""


class RepositoryError(Exception):
    """Base error for all repository operations.

    Wraps underlying DynamoDB ClientError so that internal
    details (request IDs, error codes) are never leaked to
    API consumers.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ItemNotFoundError(RepositoryError):
    """Raised when a requested item does not exist in DynamoDB."""

    def __init__(self, entity: str, key: str) -> None:
        super().__init__(f"{entity} not found: {key}")
        self.entity = entity
        self.key = key
