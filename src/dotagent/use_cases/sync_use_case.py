"""Sync use case implementing sync business logic."""

import logging
from datetime import datetime
from typing import Optional

from ..domain.entities import SyncItem
from ..domain.exceptions import (
    ConflictResolutionError,
    SyncError,
    SyncValidationError,
)
from ..domain.value_objects import (
    ConflictResolution,
    OperationResult,
    OperationStatus,
    SyncOptions,
    SyncResult,
)
from ..interfaces.repositories import GitRepository, SyncRepository
from ..interfaces.services import ConsoleService, SecurityService


class SyncUseCase:
    """Use case for sync operations.

    This class orchestrates sync operations by coordinating between
    repositories and services while implementing business rules.
    """

    def __init__(
        self,
        sync_repository: SyncRepository,
        git_repository: GitRepository,
        console_service: ConsoleService,
        security_service: SecurityService,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._sync_repo = sync_repository
        self._git_repo = git_repository
        self._console = console_service
        self._security = security_service
        self._logger = logger or logging.getLogger(__name__)

    def execute(self, options: SyncOptions) -> SyncResult:
        """Execute a sync operation with the given options.

        This is the main entry point for sync operations and implements
        the core business logic for synchronization.
        """
        start_time = datetime.now()

        try:
            return self._execute_with_error_handling(options, start_time)
        except Exception as e:
            return self._create_failure_result(options, start_time, e)

    def _execute_with_error_handling(
        self, options: SyncOptions, start_time: datetime
    ) -> SyncResult:
        """Execute sync with proper setup and validation."""
        self._logger.info(f"Starting {options.operation_type} operation")
        self._print_operation_header(options)

        # Validate preconditions
        self._validate_preconditions(options)

        # Get all sync items
        sync_items = self._sync_repo.get_sync_items()
        self._logger.info(f"Found {len(sync_items)} sync items")

        # Execute the sync operation
        operations = self._execute_sync_operation(sync_items, options)
        end_time = datetime.now()

        # Create successful result
        result = SyncResult.create_success(
            operation_type=options.operation_type,
            start_time=start_time,
            end_time=end_time,
            operations=operations,
            branch=options.branch,
            dry_run=options.dry_run,
        )

        self._log_result(result)
        return result

    def _print_operation_header(self, options: SyncOptions) -> None:
        """Print appropriate header message for the operation."""
        if options.dry_run:
            self._console.print(
                f"[bold blue]Preview: {options.operation_type}[/bold blue]"
            )
        else:
            self._console.print(
                f"[bold blue]Starting {options.operation_type}...[/bold blue]"
            )

    def _create_failure_result(
        self, options: SyncOptions, start_time: datetime, error: Exception
    ) -> SyncResult:
        """Create a failure result with proper error handling."""
        end_time = datetime.now()
        self._logger.error(f"Sync operation failed: {error}")

        result = SyncResult.create_failure(
            operation_type=options.operation_type,
            start_time=start_time,
            end_time=end_time,
            error=str(error),
            branch=options.branch,
            dry_run=options.dry_run,
        )

        self._log_result(result)
        return result

    def _validate_preconditions(self, options: SyncOptions) -> None:
        """Validate that preconditions are met for the sync operation."""
        validation_errors = []

        # Check security constraints
        if not self._security.is_safe_url(options.repository_url or ""):
            validation_errors.append("Repository URL failed security validation")

        # Check branch name
        if not options.branch or not options.branch.strip():
            validation_errors.append("Branch name cannot be empty")

        if validation_errors:
            raise SyncValidationError(validation_errors)

    def _execute_sync_operation(
        self, sync_items: list[SyncItem], options: SyncOptions
    ) -> list[OperationResult]:
        """Execute the appropriate sync operation based on options."""
        if options.is_bidirectional:
            return self._execute_bidirectional_sync(sync_items, options)

        if options.pull_only:
            return self._execute_pull_sync(sync_items, options)

        if options.push_only:
            return self._execute_push_sync(sync_items, options)

        return []

    def _execute_bidirectional_sync(
        self, sync_items: list[SyncItem], options: SyncOptions
    ) -> list[OperationResult]:
        """Execute bidirectional synchronization."""
        operations = []

        for item in sync_items:
            try:
                status = item.get_status()
                operation = self._determine_sync_operation(item, status, options)

                if operation:
                    result = self._execute_item_operation(item, operation, options)
                    operations.append(result)
                else:
                    # Item is in sync, skip
                    operations.append(
                        OperationResult(
                            item_name=item.name,
                            operation="skip",
                            status=OperationStatus.SUCCESS,
                            message="Already in sync",
                        )
                    )

            except Exception as e:
                self._logger.error(f"Failed to sync item {item.name}: {e}")
                operations.append(
                    OperationResult(
                        item_name=item.name,
                        operation="sync",
                        status=OperationStatus.FAILURE,
                        message=str(e),
                    )
                )

        return operations

    def _execute_pull_sync(
        self, sync_items: list[SyncItem], options: SyncOptions
    ) -> list[OperationResult]:
        """Execute pull-only synchronization."""
        operations = []

        for item in sync_items:
            if item.exists_remotely:
                try:
                    result = self._execute_item_operation(item, "pull", options)
                    operations.append(result)
                except Exception as e:
                    self._logger.error(f"Failed to pull item {item.name}: {e}")
                    operations.append(
                        OperationResult(
                            item_name=item.name,
                            operation="pull",
                            status=OperationStatus.FAILURE,
                            message=str(e),
                        )
                    )

        return operations

    def _execute_push_sync(
        self, sync_items: list[SyncItem], options: SyncOptions
    ) -> list[OperationResult]:
        """Execute push-only synchronization."""
        operations = []

        for item in sync_items:
            if item.exists_locally:
                try:
                    result = self._execute_item_operation(item, "push", options)
                    operations.append(result)
                except Exception as e:
                    self._logger.error(f"Failed to push item {item.name}: {e}")
                    operations.append(
                        OperationResult(
                            item_name=item.name,
                            operation="push",
                            status=OperationStatus.FAILURE,
                            message=str(e),
                        )
                    )

        return operations

    def _determine_sync_operation(
        self, item: SyncItem, status, options: SyncOptions
    ) -> Optional[str]:
        """Determine what operation should be performed on a sync item."""
        from ..domain.entities.sync_item import SyncStatus

        if status == SyncStatus.IN_SYNC:
            return None

        if status == SyncStatus.LOCAL_ONLY:
            return "push"

        if status == SyncStatus.REMOTE_ONLY:
            return "pull"

        if status in (SyncStatus.LOCAL_NEWER, SyncStatus.REMOTE_NEWER):
            return self._resolve_version_conflict(item, status, options)

        if status == SyncStatus.CONFLICT:
            return self._resolve_content_conflict(item, options)

        return None

    def _resolve_version_conflict(
        self, item: SyncItem, status, options: SyncOptions
    ) -> Optional[str]:
        """Resolve version conflicts (local/remote newer)."""
        conflict_type = (
            "local_newer" if status.name == "LOCAL_NEWER" else "remote_newer"
        )

        if options.conflict_resolution == ConflictResolution.LOCAL:
            return "push"

        if options.conflict_resolution == ConflictResolution.REMOTE:
            return "pull"

        if options.conflict_resolution == ConflictResolution.PROMPT:
            return self._prompt_for_conflict_resolution(item, conflict_type)

        return None

    def _resolve_content_conflict(
        self, item: SyncItem, options: SyncOptions
    ) -> Optional[str]:
        """Resolve content conflicts."""
        if options.conflict_resolution == ConflictResolution.ABORT:
            raise ConflictResolutionError([item.name], "abort")

        if options.conflict_resolution == ConflictResolution.PROMPT:
            return self._prompt_for_conflict_resolution(item, "conflict")

        return None

    def _prompt_for_conflict_resolution(
        self, item: SyncItem, conflict_type: str
    ) -> str:
        """Prompt user for conflict resolution."""
        message = (
            f"Conflict detected for '{item.name}' ({conflict_type}). Choose action:"
        )
        choices = ["pull (use remote)", "push (use local)", "skip"]

        choice = self._console.select(message, choices)

        choice_map = {
            "pull": "pull",
            "push": "push",
        }

        for key, operation in choice_map.items():
            if choice.startswith(key):
                return operation

        return "skip"

    def _execute_item_operation(
        self, item: SyncItem, operation: str, options: SyncOptions
    ) -> OperationResult:
        """Execute a specific operation on a sync item."""
        if options.dry_run:
            return OperationResult(
                item_name=item.name,
                operation=operation,
                status=OperationStatus.SUCCESS,
                message=f"Would {operation} {item.name}",
            )

        try:
            if operation == "pull":
                success = self._sync_repo.copy_item(item, source_to_dest=False)
            elif operation == "push":
                success = self._sync_repo.copy_item(item, source_to_dest=True)
            elif operation == "skip":
                return OperationResult(
                    item_name=item.name,
                    operation=operation,
                    status=OperationStatus.SUCCESS,
                    message="Skipped by user",
                )
            else:
                raise SyncError(f"Unknown operation: {operation}")

            if success:
                return OperationResult(
                    item_name=item.name,
                    operation=operation,
                    status=OperationStatus.SUCCESS,
                    message=f"Successfully {operation}ed {item.name}",
                )
            else:
                return OperationResult(
                    item_name=item.name,
                    operation=operation,
                    status=OperationStatus.FAILURE,
                    message=f"Failed to {operation} {item.name}",
                )

        except Exception as e:
            return OperationResult(
                item_name=item.name,
                operation=operation,
                status=OperationStatus.FAILURE,
                message=str(e),
            )

    def _log_result(self, result: SyncResult) -> None:
        """Log the sync result."""
        if result.success:
            self._console.print_success(result.get_summary_message())
            if result.has_failures:
                failure_summary = result.get_failure_summary()
                if failure_summary:
                    self._console.print_warning(failure_summary)
        else:
            self._console.print_error(f"Sync failed: {result.error}")

        self._logger.info(
            f"Sync completed: {result.items_succeeded} succeeded, "
            f"{result.items_failed} failed, duration: {result.duration:.2f}s"
        )
