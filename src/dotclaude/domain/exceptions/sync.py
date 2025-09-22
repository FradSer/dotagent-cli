"""Sync operation exceptions."""

from typing import Optional

from .base import DomainError


class SyncError(DomainError):
    """Base class for sync operation errors."""

    pass


class ConflictResolutionError(SyncError):
    """Raised when conflict resolution fails or is ambiguous."""

    def __init__(
        self, conflicted_items: list[str], resolution_strategy: Optional[str] = None
    ) -> None:
        message = f"Failed to resolve conflicts for {len(conflicted_items)} item(s): {', '.join(conflicted_items[:3])}"
        if len(conflicted_items) > 3:
            message += f" and {len(conflicted_items) - 3} more"

        if resolution_strategy:
            message += f" using strategy '{resolution_strategy}'"

        suggestion = (
            "Review the conflicted files manually or use --prefer local/remote "
            "to specify conflict resolution preference."
        )

        super().__init__(
            message=message,
            details={
                "conflicted_items": conflicted_items,
                "resolution_strategy": resolution_strategy,
            },
            suggestion=suggestion,
        )


class SyncValidationError(SyncError):
    """Raised when sync operation validation fails."""

    def __init__(
        self, validation_failures: list[str], operation: Optional[str] = None
    ) -> None:
        message = f"Sync validation failed: {', '.join(validation_failures)}"
        if operation:
            message = f"{operation} validation failed: {', '.join(validation_failures)}"

        suggestion = "Fix the validation errors and try again."

        super().__init__(
            message=message,
            details={
                "validation_failures": validation_failures,
                "operation": operation,
            },
            suggestion=suggestion,
        )


class SyncItemNotFoundError(SyncError):
    """Raised when a sync item is not found in expected location."""

    def __init__(self, item_name: str, location: str) -> None:
        message = f"Sync item '{item_name}' not found in {location}"
        suggestion = f"Check that '{item_name}' exists in the expected location"

        super().__init__(
            message=message,
            details={"item_name": item_name, "location": location},
            suggestion=suggestion,
        )


class UnsupportedSyncOperationError(SyncError):
    """Raised when attempting an unsupported sync operation."""

    def __init__(self, operation: str, item_type: Optional[str] = None) -> None:
        message = f"Unsupported sync operation: {operation}"
        if item_type:
            message += f" for item type '{item_type}'"

        suggestion = "Check the documentation for supported sync operations"

        super().__init__(
            message=message,
            details={"operation": operation, "item_type": item_type},
            suggestion=suggestion,
        )
