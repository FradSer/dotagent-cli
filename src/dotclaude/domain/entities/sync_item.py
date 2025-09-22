"""Sync item entity representing items that can be synchronized."""

import hashlib
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from ..constants import Performance
from ..exceptions import SyncValidationError


class SyncItemType(Enum):
    """Types of items that can be synchronized."""

    FILE = "file"
    DIRECTORY = "directory"
    SYMLINK = "symlink"


class SyncStatus(Enum):
    """Synchronization status of an item."""

    IN_SYNC = "in_sync"
    LOCAL_NEWER = "local_newer"
    REMOTE_NEWER = "remote_newer"
    CONFLICT = "conflict"
    LOCAL_ONLY = "local_only"
    REMOTE_ONLY = "remote_only"
    DIFFERENT = "different"


@dataclass(frozen=True)
class SyncItem:
    """Represents an item that can be synchronized between local and remote locations.

    This is a core domain entity that encapsulates the business logic
    for determining sync status and handling sync operations.
    """

    name: str
    item_type: SyncItemType
    local_path: Path
    remote_path: Path

    def __post_init__(self) -> None:
        """Validate the sync item after initialization."""
        if not self.name:
            raise SyncValidationError(["Name cannot be empty"])

        if not self.name.replace("-", "").replace("_", "").replace(".", "").isalnum():
            raise SyncValidationError([f"Invalid item name: {self.name}"])

    @property
    def exists_locally(self) -> bool:
        """Check if the item exists in the local location."""
        return self.local_path.exists()

    @property
    def exists_remotely(self) -> bool:
        """Check if the item exists in the remote location."""
        return self.remote_path.exists()

    @property
    def local_size(self) -> Optional[int]:
        """Get the size of the local item in bytes."""
        if not self.exists_locally:
            return None

        if self.item_type == SyncItemType.FILE:
            return self.local_path.stat().st_size
        elif self.item_type == SyncItemType.DIRECTORY:
            return sum(
                f.stat().st_size for f in self.local_path.rglob("*") if f.is_file()
            )
        return None

    @property
    def remote_size(self) -> Optional[int]:
        """Get the size of the remote item in bytes."""
        if not self.exists_remotely:
            return None

        if self.item_type == SyncItemType.FILE:
            return self.remote_path.stat().st_size
        elif self.item_type == SyncItemType.DIRECTORY:
            return sum(
                f.stat().st_size for f in self.remote_path.rglob("*") if f.is_file()
            )
        return None

    @property
    def local_modified_time(self) -> Optional[datetime]:
        """Get the last modification time of the local item."""
        if not self.exists_locally:
            return None
        return datetime.fromtimestamp(self.local_path.stat().st_mtime)

    @property
    def remote_modified_time(self) -> Optional[datetime]:
        """Get the last modification time of the remote item."""
        if not self.exists_remotely:
            return None
        return datetime.fromtimestamp(self.remote_path.stat().st_mtime)

    def get_local_checksum(self) -> Optional[str]:
        """Calculate checksum of the local item."""
        if not self.exists_locally or self.item_type != SyncItemType.FILE:
            return None

        hash_md5 = hashlib.md5()
        with open(self.local_path, "rb") as f:
            for chunk in iter(lambda: f.read(Performance.FILE_READ_BUFFER_SIZE), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_remote_checksum(self) -> Optional[str]:
        """Calculate checksum of the remote item."""
        if not self.exists_remotely or self.item_type != SyncItemType.FILE:
            return None

        hash_md5 = hashlib.md5()
        with open(self.remote_path, "rb") as f:
            for chunk in iter(lambda: f.read(Performance.FILE_READ_BUFFER_SIZE), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_status(self) -> SyncStatus:
        """Determine the synchronization status of this item."""
        local_exists = self.exists_locally
        remote_exists = self.exists_remotely

        # Handle existence combinations
        if not local_exists and not remote_exists:
            return SyncStatus.IN_SYNC  # Both don't exist

        if local_exists and not remote_exists:
            return SyncStatus.LOCAL_ONLY

        if not local_exists and remote_exists:
            return SyncStatus.REMOTE_ONLY

        # Both exist - check if they're different
        if self.item_type == SyncItemType.FILE:
            local_checksum = self.get_local_checksum()
            remote_checksum = self.get_remote_checksum()

            if local_checksum == remote_checksum:
                return SyncStatus.IN_SYNC

            # Files are different, determine which is newer
            local_time = self.local_modified_time
            remote_time = self.remote_modified_time

            if local_time and remote_time:
                if local_time > remote_time:
                    return SyncStatus.LOCAL_NEWER
                elif remote_time > local_time:
                    return SyncStatus.REMOTE_NEWER
                else:
                    return SyncStatus.CONFLICT  # Same time, different content

            return SyncStatus.DIFFERENT

        elif self.item_type == SyncItemType.DIRECTORY:
            # For directories, we'll need to compare contents
            # This is a simplified check - in practice, you'd want to
            # recursively compare directory contents
            local_time = self.local_modified_time
            remote_time = self.remote_modified_time

            if local_time and remote_time:
                if abs((local_time - remote_time).total_seconds()) < 1:
                    return SyncStatus.IN_SYNC
                elif local_time > remote_time:
                    return SyncStatus.LOCAL_NEWER
                else:
                    return SyncStatus.REMOTE_NEWER

            return SyncStatus.DIFFERENT

        return SyncStatus.DIFFERENT

    def needs_sync(self) -> bool:
        """Check if this item needs synchronization."""
        status = self.get_status()
        return status not in [SyncStatus.IN_SYNC]

    def to_dict(self) -> dict[str, Any]:
        """Convert the sync item to a dictionary representation."""
        return {
            "name": self.name,
            "type": self.item_type.value,
            "local_path": str(self.local_path),
            "remote_path": str(self.remote_path),
            "status": self.get_status().value,
            "exists_locally": self.exists_locally,
            "exists_remotely": self.exists_remotely,
            "local_size": self.local_size,
            "remote_size": self.remote_size,
            "local_modified": self.local_modified_time.isoformat()
            if self.local_modified_time
            else None,
            "remote_modified": self.remote_modified_time.isoformat()
            if self.remote_modified_time
            else None,
        }
