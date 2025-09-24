"""Unit tests for SyncUseCase."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from dotagent.use_cases.sync_use_case import SyncUseCase
from dotagent.domain.value_objects import SyncOptions, ConflictResolution
from dotagent.domain.entities.sync_item import SyncStatus
from dotagent.domain.exceptions import SyncValidationError


class TestSyncUseCase:
    """Test cases for SyncUseCase."""

    @pytest.fixture
    def sync_use_case(self, all_mocks: dict) -> SyncUseCase:
        """Create SyncUseCase with mocked dependencies."""
        return SyncUseCase(
            sync_repository=all_mocks["sync_repository"],
            git_repository=all_mocks["git_repository"],
            console_service=all_mocks["console_service"],
            security_service=all_mocks["security_service"],
        )

    def test_execute_successful_sync(
        self,
        sync_use_case: SyncUseCase,
        sync_options: SyncOptions,
        all_mocks: dict,
        sample_sync_item,
    ) -> None:
        """Test successful sync execution."""
        # Setup mocks
        all_mocks["sync_repository"].get_sync_items.return_value = [sample_sync_item]
        all_mocks["sync_repository"].copy_item.return_value = True
        all_mocks["security_service"].is_safe_url.return_value = True

        # Execute
        result = sync_use_case.execute(sync_options)

        # Verify
        assert result.success is True
        assert result.operation_type == sync_options.operation_type
        assert result.items_processed >= 0
        assert isinstance(result.start_time, datetime)
        assert isinstance(result.end_time, datetime)

    def test_execute_with_dry_run(
        self,
        sync_use_case: SyncUseCase,
        all_mocks: dict,
        sample_sync_item,
    ) -> None:
        """Test sync execution with dry run."""
        options = SyncOptions(dry_run=True)
        all_mocks["sync_repository"].get_sync_items.return_value = [sample_sync_item]
        all_mocks["security_service"].is_safe_url.return_value = True

        result = sync_use_case.execute(options)

        assert result.success is True
        assert result.dry_run is True
        # Should not call actual copy operations in dry run
        all_mocks["sync_repository"].copy_item.assert_not_called()

    def test_execute_with_validation_error(
        self,
        sync_use_case: SyncUseCase,
        all_mocks: dict,
    ) -> None:
        """Test sync execution with validation errors."""
        options = SyncOptions(repository_url="https://github.com/user/repo")
        all_mocks["security_service"].is_safe_url.return_value = False

        result = sync_use_case.execute(options)

        assert result.success is False
        assert "security validation" in result.error.lower()

    def test_execute_pull_only_sync(
        self,
        sync_use_case: SyncUseCase,
        all_mocks: dict,
        sample_sync_item,
    ) -> None:
        """Test pull-only sync execution."""
        options = SyncOptions(pull_only=True)
        all_mocks["sync_repository"].get_sync_items.return_value = [sample_sync_item]
        all_mocks["security_service"].is_safe_url.return_value = True

        result = sync_use_case.execute(options)

        assert result.success is True
        assert result.operation_type == "pull"

    def test_execute_push_only_sync(
        self,
        sync_use_case: SyncUseCase,
        all_mocks: dict,
        sample_sync_item,
    ) -> None:
        """Test push-only sync execution."""
        options = SyncOptions(push_only=True)
        all_mocks["sync_repository"].get_sync_items.return_value = [sample_sync_item]
        all_mocks["security_service"].is_safe_url.return_value = True

        result = sync_use_case.execute(options)

        assert result.success is True
        assert result.operation_type == "push"

    def test_conflict_resolution_prefer_local(
        self,
        sync_use_case: SyncUseCase,
        all_mocks: dict,
        sample_sync_item,
    ) -> None:
        """Test conflict resolution preferring local."""
        options = SyncOptions(conflict_resolution=ConflictResolution.LOCAL)
        all_mocks["sync_repository"].get_sync_items.return_value = [sample_sync_item]
        all_mocks["security_service"].is_safe_url.return_value = True

        # Mock the sync item to have a conflict
        with patch.object(
            sample_sync_item, "get_status", return_value=SyncStatus.CONFLICT
        ):
            result = sync_use_case.execute(options)

        assert result.success is True

    def test_conflict_resolution_prefer_remote(
        self,
        sync_use_case: SyncUseCase,
        all_mocks: dict,
        sample_sync_item,
    ) -> None:
        """Test conflict resolution preferring remote."""
        options = SyncOptions(conflict_resolution=ConflictResolution.REMOTE)
        all_mocks["sync_repository"].get_sync_items.return_value = [sample_sync_item]
        all_mocks["security_service"].is_safe_url.return_value = True

        # Mock the sync item to have a conflict
        with patch.object(
            sample_sync_item, "get_status", return_value=SyncStatus.CONFLICT
        ):
            result = sync_use_case.execute(options)

        assert result.success is True

    def test_conflict_resolution_prompt(
        self,
        sync_use_case: SyncUseCase,
        all_mocks: dict,
        sample_sync_item,
    ) -> None:
        """Test conflict resolution with user prompt."""
        options = SyncOptions(conflict_resolution=ConflictResolution.PROMPT)
        all_mocks["sync_repository"].get_sync_items.return_value = [sample_sync_item]
        all_mocks["security_service"].is_safe_url.return_value = True
        all_mocks["console_service"].select.return_value = "pull (use remote)"

        # Mock the sync item to have a conflict
        with patch.object(
            sample_sync_item, "get_status", return_value=SyncStatus.CONFLICT
        ):
            result = sync_use_case.execute(options)

        assert result.success is True
        all_mocks["console_service"].select.assert_called()

    def test_sync_repository_error_handling(
        self,
        sync_use_case: SyncUseCase,
        all_mocks: dict,
        sample_sync_item,
    ) -> None:
        """Test error handling when sync repository fails."""
        options = SyncOptions()
        all_mocks["sync_repository"].get_sync_items.return_value = [sample_sync_item]
        all_mocks["sync_repository"].copy_item.side_effect = Exception("Copy failed")
        all_mocks["security_service"].is_safe_url.return_value = True

        result = sync_use_case.execute(options)

        # Should still return a result, but with failures recorded
        assert isinstance(result.start_time, datetime)
        assert isinstance(result.end_time, datetime)

    def test_empty_sync_items_list(
        self,
        sync_use_case: SyncUseCase,
        all_mocks: dict,
    ) -> None:
        """Test sync with empty items list."""
        options = SyncOptions()
        all_mocks["sync_repository"].get_sync_items.return_value = []
        all_mocks["security_service"].is_safe_url.return_value = True

        result = sync_use_case.execute(options)

        assert result.success is True
        assert result.items_processed == 0
        assert len(result.operations) == 0

    def test_sync_item_already_in_sync(
        self,
        sync_use_case: SyncUseCase,
        all_mocks: dict,
        sample_sync_item,
    ) -> None:
        """Test sync item that's already in sync."""
        options = SyncOptions()
        all_mocks["sync_repository"].get_sync_items.return_value = [sample_sync_item]
        all_mocks["security_service"].is_safe_url.return_value = True

        # Mock the item as already in sync
        with patch.object(
            sample_sync_item, "get_status", return_value=SyncStatus.IN_SYNC
        ):
            result = sync_use_case.execute(options)

        assert result.success is True
        # Should have a "skip" operation for the in-sync item
        skip_operations = [op for op in result.operations if op.operation == "skip"]
        assert len(skip_operations) > 0
