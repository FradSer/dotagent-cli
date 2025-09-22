"""Sync operation result value objects."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class OperationStatus(Enum):
    """Status of an operation."""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class OperationResult:
    """Result of a single operation within a sync."""

    item_name: str
    operation: str  # "copy", "delete", "skip", etc.
    status: OperationStatus
    message: Optional[str] = None
    details: Optional[dict[str, Any]] = None

    @property
    def success(self) -> bool:
        """Check if the operation was successful."""
        return self.status == OperationStatus.SUCCESS

    @property
    def failed(self) -> bool:
        """Check if the operation failed."""
        return self.status == OperationStatus.FAILURE


@dataclass(frozen=True)
class SyncResult:
    """Value object representing the result of a sync operation.

    This immutable object contains all information about what happened
    during a sync operation, including successes, failures, and metadata.
    """

    # Overall status
    success: bool
    operation_type: str  # "pull", "push", "bidirectional"

    # Timing
    start_time: datetime
    end_time: datetime

    # Results
    operations: list[OperationResult]

    # Summary counts
    items_processed: int = 0
    items_succeeded: int = 0
    items_failed: int = 0
    items_skipped: int = 0

    # Error information
    error: Optional[str] = None
    error_details: Optional[dict[str, Any]] = None

    # Additional metadata
    branch: Optional[str] = None
    repository_url: Optional[str] = None
    dry_run: bool = False

    def __post_init__(self) -> None:
        """Calculate derived values after initialization."""
        # Calculate counts from operations if not provided
        if not self.items_processed and self.operations:
            object.__setattr__(self, "items_processed", len(self.operations))

        if not self.items_succeeded and self.operations:
            succeeded = sum(1 for op in self.operations if op.success)
            object.__setattr__(self, "items_succeeded", succeeded)

        if not self.items_failed and self.operations:
            failed = sum(1 for op in self.operations if op.failed)
            object.__setattr__(self, "items_failed", failed)

    @property
    def duration(self) -> float:
        """Get the duration of the sync operation in seconds."""
        return (self.end_time - self.start_time).total_seconds()

    @property
    def success_rate(self) -> float:
        """Get the success rate as a percentage (0-100)."""
        if self.items_processed == 0:
            return 100.0
        return (self.items_succeeded / self.items_processed) * 100

    @property
    def failed_operations(self) -> list[OperationResult]:
        """Get list of failed operations."""
        return [op for op in self.operations if op.failed]

    @property
    def successful_operations(self) -> list[OperationResult]:
        """Get list of successful operations."""
        return [op for op in self.operations if op.success]

    @property
    def has_failures(self) -> bool:
        """Check if there were any failures."""
        return self.items_failed > 0

    @property
    def is_complete_success(self) -> bool:
        """Check if all operations succeeded."""
        return self.success and self.items_failed == 0

    @property
    def is_partial_success(self) -> bool:
        """Check if some operations succeeded but some failed."""
        return self.items_succeeded > 0 and self.items_failed > 0

    def get_summary_message(self) -> str:
        """Get a human-readable summary of the sync result."""
        if self.dry_run:
            prefix = "Preview: "
        else:
            prefix = ""

        if self.is_complete_success:
            return f"{prefix}Successfully {self.operation_type} {self.items_succeeded} item(s)"
        elif self.is_partial_success:
            return (
                f"{prefix}Partially completed {self.operation_type}: "
                f"{self.items_succeeded} succeeded, {self.items_failed} failed"
            )
        elif self.has_failures:
            return f"{prefix}Failed to {self.operation_type}: {self.error or 'Multiple errors occurred'}"
        else:
            return f"{prefix}No items to {self.operation_type}"

    def get_failure_summary(self) -> Optional[str]:
        """Get a summary of failures if any occurred."""
        if not self.has_failures:
            return None

        failed_items = [op.item_name for op in self.failed_operations]
        if len(failed_items) <= 3:
            return f"Failed items: {', '.join(failed_items)}"
        else:
            shown = ", ".join(failed_items[:3])
            remaining = len(failed_items) - 3
            return f"Failed items: {shown} and {remaining} more"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "operation_type": self.operation_type,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration": self.duration,
            "items_processed": self.items_processed,
            "items_succeeded": self.items_succeeded,
            "items_failed": self.items_failed,
            "items_skipped": self.items_skipped,
            "success_rate": self.success_rate,
            "error": self.error,
            "error_details": self.error_details,
            "branch": self.branch,
            "repository_url": self.repository_url,
            "dry_run": self.dry_run,
            "operations": [
                {
                    "item_name": op.item_name,
                    "operation": op.operation,
                    "status": op.status.value,
                    "message": op.message,
                    "details": op.details,
                }
                for op in self.operations
            ],
        }

    @classmethod
    def create_success(
        cls,
        operation_type: str,
        start_time: datetime,
        end_time: datetime,
        operations: list[OperationResult],
        **kwargs,
    ) -> "SyncResult":
        """Create a successful sync result."""
        return cls(
            success=True,
            operation_type=operation_type,
            start_time=start_time,
            end_time=end_time,
            operations=operations,
            **kwargs,
        )

    @classmethod
    def create_failure(
        cls,
        operation_type: str,
        start_time: datetime,
        end_time: datetime,
        error: str,
        operations: Optional[list[OperationResult]] = None,
        **kwargs,
    ) -> "SyncResult":
        """Create a failed sync result."""
        return cls(
            success=False,
            operation_type=operation_type,
            start_time=start_time,
            end_time=end_time,
            operations=operations or [],
            error=error,
            **kwargs,
        )
