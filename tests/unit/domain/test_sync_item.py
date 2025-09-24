"""Unit tests for SyncItem domain entity."""

import pytest
from pathlib import Path
from datetime import datetime

from dotagent.domain.entities.sync_item import SyncItem, SyncItemType, SyncStatus
from dotagent.domain.exceptions import SyncValidationError


class TestSyncItem:
    """Test cases for SyncItem entity."""

    def test_create_valid_sync_item(self, temp_dir: Path) -> None:
        """Test creating a valid sync item."""
        local_path = temp_dir / "local" / "test.md"
        remote_path = temp_dir / "remote" / "test.md"

        item = SyncItem(
            name="test.md",
            item_type=SyncItemType.FILE,
            local_path=local_path,
            remote_path=remote_path,
        )

        assert item.name == "test.md"
        assert item.item_type == SyncItemType.FILE
        assert item.local_path == local_path
        assert item.remote_path == remote_path

    def test_invalid_name_raises_validation_error(self, temp_dir: Path) -> None:
        """Test that invalid names raise validation errors."""
        local_path = temp_dir / "local" / "test.md"
        remote_path = temp_dir / "remote" / "test.md"

        with pytest.raises(SyncValidationError):
            SyncItem(
                name="",  # Empty name
                item_type=SyncItemType.FILE,
                local_path=local_path,
                remote_path=remote_path,
            )

        with pytest.raises(SyncValidationError):
            SyncItem(
                name="invalid/name",  # Contains slash
                item_type=SyncItemType.FILE,
                local_path=local_path,
                remote_path=remote_path,
            )

    def test_exists_locally_when_file_exists(self, sample_sync_item: SyncItem) -> None:
        """Test exists_locally property when file exists."""
        assert sample_sync_item.exists_locally is True

    def test_exists_locally_when_file_missing(self, temp_dir: Path) -> None:
        """Test exists_locally property when file is missing."""
        item = SyncItem(
            name="missing.md",
            item_type=SyncItemType.FILE,
            local_path=temp_dir / "missing.md",
            remote_path=temp_dir / "remote.md",
        )
        assert item.exists_locally is False

    def test_get_status_in_sync_when_identical(self, temp_dir: Path) -> None:
        """Test status when local and remote are identical."""
        content = "# Test\n\nIdentical content"

        local_path = temp_dir / "local.md"
        remote_path = temp_dir / "remote.md"

        local_path.write_text(content)
        remote_path.write_text(content)

        item = SyncItem(
            name="test.md",
            item_type=SyncItemType.FILE,
            local_path=local_path,
            remote_path=remote_path,
        )

        assert item.get_status() == SyncStatus.IN_SYNC

    def test_get_status_local_only(self, temp_dir: Path) -> None:
        """Test status when only local file exists."""
        local_path = temp_dir / "local.md"
        remote_path = temp_dir / "remote.md"

        local_path.write_text("Local content")
        # Don't create remote file

        item = SyncItem(
            name="test.md",
            item_type=SyncItemType.FILE,
            local_path=local_path,
            remote_path=remote_path,
        )

        assert item.get_status() == SyncStatus.LOCAL_ONLY

    def test_get_status_remote_only(self, temp_dir: Path) -> None:
        """Test status when only remote file exists."""
        local_path = temp_dir / "local.md"
        remote_path = temp_dir / "remote.md"

        # Don't create local file
        remote_path.write_text("Remote content")

        item = SyncItem(
            name="test.md",
            item_type=SyncItemType.FILE,
            local_path=local_path,
            remote_path=remote_path,
        )

        assert item.get_status() == SyncStatus.REMOTE_ONLY

    def test_get_status_different_content(self, temp_dir: Path) -> None:
        """Test status when files have different content."""
        local_path = temp_dir / "local.md"
        remote_path = temp_dir / "remote.md"

        local_path.write_text("Local content")
        remote_path.write_text("Remote content")

        item = SyncItem(
            name="test.md",
            item_type=SyncItemType.FILE,
            local_path=local_path,
            remote_path=remote_path,
        )

        status = item.get_status()
        assert status in [
            SyncStatus.LOCAL_NEWER,
            SyncStatus.REMOTE_NEWER,
            SyncStatus.DIFFERENT,
        ]

    def test_needs_sync_when_out_of_sync(self, temp_dir: Path) -> None:
        """Test needs_sync when files are out of sync."""
        local_path = temp_dir / "local.md"
        remote_path = temp_dir / "remote.md"

        local_path.write_text("Different")
        remote_path.write_text("Content")

        item = SyncItem(
            name="test.md",
            item_type=SyncItemType.FILE,
            local_path=local_path,
            remote_path=remote_path,
        )

        assert item.needs_sync() is True

    def test_needs_sync_when_in_sync(self, temp_dir: Path) -> None:
        """Test needs_sync when files are in sync."""
        content = "Same content"
        local_path = temp_dir / "local.md"
        remote_path = temp_dir / "remote.md"

        local_path.write_text(content)
        remote_path.write_text(content)

        item = SyncItem(
            name="test.md",
            item_type=SyncItemType.FILE,
            local_path=local_path,
            remote_path=remote_path,
        )

        assert item.needs_sync() is False

    def test_to_dict_serialization(self, sample_sync_item: SyncItem) -> None:
        """Test converting sync item to dictionary."""
        data = sample_sync_item.to_dict()

        assert data["name"] == sample_sync_item.name
        assert data["type"] == sample_sync_item.item_type.value
        assert data["local_path"] == str(sample_sync_item.local_path)
        assert data["remote_path"] == str(sample_sync_item.remote_path)
        assert "status" in data
        assert "exists_locally" in data
        assert "exists_remotely" in data

    def test_checksum_calculation(self, temp_dir: Path) -> None:
        """Test checksum calculation for files."""
        content = "Test content for checksum"
        local_path = temp_dir / "test.md"
        local_path.write_text(content)

        item = SyncItem(
            name="test.md",
            item_type=SyncItemType.FILE,
            local_path=local_path,
            remote_path=temp_dir / "remote.md",
        )

        checksum = item.get_local_checksum()
        assert checksum is not None
        assert len(checksum) == 32  # MD5 hash length

    def test_checksum_none_for_missing_file(self, temp_dir: Path) -> None:
        """Test checksum is None for missing files."""
        item = SyncItem(
            name="missing.md",
            item_type=SyncItemType.FILE,
            local_path=temp_dir / "missing.md",
            remote_path=temp_dir / "remote.md",
        )

        assert item.get_local_checksum() is None

    def test_size_calculation(self, sample_sync_item: SyncItem) -> None:
        """Test size calculation for files."""
        size = sample_sync_item.local_size
        assert size is not None
        assert size > 0
