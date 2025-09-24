"""Sync-related domain exceptions."""


class SyncValidationError(ValueError):
    """Raised when sync item validation fails."""

    def __init__(self, message: str, item_name: str = None):
        super().__init__(message)
        self.item_name = item_name


class SyncExecutionError(RuntimeError):
    """Raised when sync execution fails."""

    def __init__(self, message: str, item_name: str = None, cause: Exception = None):
        super().__init__(message)
        self.item_name = item_name
        self.cause = cause
