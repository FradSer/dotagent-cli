"""Sync item domain entity."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class SyncItemType(Enum):
    """Types of sync items."""

    FILE = "file"
    DIRECTORY = "dir"


class SyncStatus(Enum):
    """Status of sync items."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"


class SyncItem(BaseModel):
    """Domain entity representing a sync item."""

    name: str = Field(min_length=1, max_length=100)
    type: SyncItemType
    local_path: Optional[Path] = None
    remote_path: Optional[Path] = None
    status: SyncStatus = SyncStatus.PENDING
    last_synced: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = {
        "frozen": True,  # Make immutable
        "use_enum_values": True,
        "validate_assignment": True,
        "arbitrary_types_allowed": True,  # Allow Path type
    }

    def with_status(self, status: SyncStatus, error_message: Optional[str] = None) -> "SyncItem":
        """Create a new SyncItem with updated status."""
        return SyncItem(
            name=self.name,
            type=self.type,
            local_path=self.local_path,
            remote_path=self.remote_path,
            status=status,
            last_synced=datetime.now() if status == SyncStatus.SUCCESS else self.last_synced,
            error_message=error_message,
        )

    def is_successful(self) -> bool:
        """Check if the sync was successful."""
        return self.status == SyncStatus.SUCCESS

    def has_local_path(self) -> bool:
        """Check if local path exists."""
        return self.local_path is not None and self.local_path.exists()

    def has_remote_path(self) -> bool:
        """Check if remote path exists."""
        return self.remote_path is not None and self.remote_path.exists()
