"""Sync strategy implementations for different operation types."""

import os
from abc import ABC, abstractmethod
from pathlib import Path

from dotclaude.core.git_manager import GitManager
from dotclaude.domain.constants import Git
from dotclaude.domain.value_objects import ConflictResolution, SyncOptions
from dotclaude.domain.value_objects.sync_result import OperationResult, OperationStatus
from dotclaude.utils.console import console


class SyncStrategy(ABC):
    """Abstract base class for sync strategies."""

    def __init__(self, git_manager: GitManager, sync_items: list, claude_dir: Path):
        self.git_manager = git_manager
        self.sync_items = sync_items
        self.claude_dir = claude_dir

    @abstractmethod
    def execute(self, working_dir: Path, options: SyncOptions) -> list[OperationResult]:
        """Execute the sync strategy."""
        pass

    def _create_operation_result(
        self, item_name: str, operation: str, success: bool, message: str
    ) -> OperationResult:
        """Create an OperationResult with consistent structure."""
        status = OperationStatus.SUCCESS if success else OperationStatus.FAILURE
        return OperationResult(
            item_name=item_name, operation=operation, status=status, message=message
        )

    def _handle_missing_item(self, item_name: str, location: str) -> OperationResult:
        """Handle missing item during sync."""
        console.print(f"[warning]Item not found {location}: {item_name}[/warning]")
        return self._create_operation_result(
            item_name, "skip", False, f"Item not found {location}"
        )

    def _handle_dry_run_operation(
        self, item_name: str, operation: str, description: str
    ) -> OperationResult:
        """Handle dry-run preview operations."""
        console.print(f"[highlight]Would {description}: {item_name}[/highlight]")
        return self._create_operation_result(
            item_name, operation, True, f"Would {description}"
        )


class PullSyncStrategy(SyncStrategy):
    """Strategy for pull-only synchronization."""

    def execute(self, working_dir: Path, options: SyncOptions) -> list[OperationResult]:
        """Pull changes from repository to local."""
        console.print("[info]Pulling changes from repository...[/info]")
        operations = []

        # Ensure ~/.claude directory exists
        self.claude_dir.mkdir(exist_ok=True)

        for item_name, item_type in self.sync_items:
            result = self._process_pull_item(working_dir, item_name, item_type, options)
            operations.append(result)

        return operations

    def _process_pull_item(
        self, working_dir: Path, item_name: str, item_type: str, options: SyncOptions
    ) -> OperationResult:
        """Process a single item for pull operation."""
        from dotclaude.core.sync_utils import SyncFileOperations

        remote_path = working_dir / item_name
        local_path = self.claude_dir / item_name

        if not remote_path.exists():
            return self._handle_missing_item(item_name, "in repository")

        file_ops = SyncFileOperations()
        is_dir = item_type == "dir"

        if options.dry_run:
            if not local_path.exists():
                return self._handle_dry_run_operation(item_name, "create", "create")
            elif not file_ops.paths_identical(local_path, remote_path, is_dir):
                return self._handle_dry_run_operation(item_name, "update", "update")
            return self._create_operation_result(
                item_name, "skip", True, "No changes needed"
            )

        # Actual sync
        if not local_path.exists():
            console.print(f"[success]Creating: {item_name}[/success]")
            file_ops.copy_path(remote_path, local_path, is_dir)
            return self._create_operation_result(
                item_name, "create", True, "Created successfully"
            )
        elif not file_ops.paths_identical(local_path, remote_path, is_dir):
            if options.force or self._prompt_overwrite(item_name):
                console.print(f"[success]Updating: {item_name}[/success]")
                file_ops.remove_path(local_path, is_dir)
                file_ops.copy_path(remote_path, local_path, is_dir)
                return self._create_operation_result(
                    item_name, "update", True, "Updated successfully"
                )
            else:
                console.print(f"[info]Skipping: {item_name}[/info]")
                return self._create_operation_result(
                    item_name, "skip", True, "Skipped by user choice"
                )

        return self._create_operation_result(
            item_name, "skip", True, "No changes needed"
        )

    def _prompt_overwrite(self, item_name: str) -> bool:
        """Prompt user for overwrite confirmation."""
        # For now, just return True (will implement interactive prompts later)
        return True


class PushSyncStrategy(SyncStrategy):
    """Strategy for push-only synchronization."""

    def execute(self, working_dir: Path, options: SyncOptions) -> list[OperationResult]:
        """Push changes from local to repository."""
        console.print("[info]Pushing changes to repository...[/info]")
        operations = []
        changes_made = 0

        os.chdir(working_dir)

        for item_name, item_type in self.sync_items:
            result = self._process_push_item(working_dir, item_name, item_type, options)
            operations.append(result)
            if result.status == OperationStatus.SUCCESS and result.operation in [
                "create",
                "update",
            ]:
                changes_made += 1

        # Commit and push changes if there are any
        if changes_made > 0 and not options.dry_run:
            self.git_manager.stage_all_changes()
            self.git_manager.create_commit(Git.COMMIT_MESSAGES["sync"])
            self.git_manager.push_changes(options.branch)

        return operations

    def _process_push_item(
        self, working_dir: Path, item_name: str, item_type: str, options: SyncOptions
    ) -> OperationResult:
        """Process a single item for push operation."""
        from dotclaude.core.sync_utils import SyncFileOperations

        local_path = self.claude_dir / item_name
        remote_path = working_dir / item_name

        if not local_path.exists():
            return self._handle_missing_item(item_name, "locally")

        file_ops = SyncFileOperations()
        is_dir = item_type == "dir"

        if options.dry_run:
            if not remote_path.exists():
                return self._handle_dry_run_operation(
                    item_name, "create", "create in repo"
                )
            elif not file_ops.paths_identical(local_path, remote_path, is_dir):
                return self._handle_dry_run_operation(
                    item_name, "update", "update in repo"
                )
            return self._create_operation_result(
                item_name, "skip", True, "No changes needed"
            )

        # Actual sync
        if not remote_path.exists():
            console.print(f"[success]Creating in repo: {item_name}[/success]")
            file_ops.copy_path(local_path, remote_path, is_dir)
            return self._create_operation_result(
                item_name, "create", True, "Created in repo successfully"
            )
        elif not file_ops.paths_identical(local_path, remote_path, is_dir):
            if options.force or self._prompt_overwrite(f"{item_name} in repo"):
                console.print(f"[success]Updating in repo: {item_name}[/success]")
                file_ops.remove_path(remote_path, is_dir)
                file_ops.copy_path(local_path, remote_path, is_dir)
                return self._create_operation_result(
                    item_name, "update", True, "Updated in repo successfully"
                )
            else:
                console.print(f"[info]Skipping: {item_name}[/info]")
                return self._create_operation_result(
                    item_name, "skip", True, "Skipped by user choice"
                )

        return self._create_operation_result(
            item_name, "skip", True, "No changes needed"
        )

    def _prompt_overwrite(self, item_name: str) -> bool:
        """Prompt user for overwrite confirmation."""
        # For now, just return True (will implement interactive prompts later)
        return True


class BidirectionalSyncStrategy(SyncStrategy):
    """Strategy for bidirectional synchronization."""

    def execute(self, working_dir: Path, options: SyncOptions) -> list[OperationResult]:
        """Perform bidirectional synchronization."""
        console.print("[info]Performing bidirectional sync...[/info]")
        operations = []
        changes_made = 0

        # Ensure ~/.claude directory exists
        self.claude_dir.mkdir(exist_ok=True)
        os.chdir(working_dir)

        for item_name, item_type in self.sync_items:
            result = self._process_bidirectional_item(
                working_dir, item_name, item_type, options
            )
            operations.append(result)
            if result.status == OperationStatus.SUCCESS and result.operation in [
                "use_local",
                "use_remote",
                "copy_to_repo",
                "copy_to_local",
            ]:
                changes_made += 1

        # Commit and push if there are changes
        if changes_made > 0 and not options.dry_run:
            self.git_manager.stage_all_changes()
            self.git_manager.create_commit(Git.COMMIT_MESSAGES["bidirectional"])
            self.git_manager.push_changes(options.branch)

        return operations

    def _process_bidirectional_item(
        self, working_dir: Path, item_name: str, item_type: str, options: SyncOptions
    ) -> OperationResult:
        """Process a single item for bidirectional operation."""
        from dotclaude.core.sync_utils import SyncFileOperations

        local_path = self.claude_dir / item_name
        remote_path = working_dir / item_name
        file_ops = SyncFileOperations()
        is_dir = item_type == "dir"

        local_exists = local_path.exists()
        remote_exists = remote_path.exists()

        if local_exists and remote_exists:
            return self._handle_conflict(
                item_name, local_path, remote_path, is_dir, options, file_ops
            )
        elif local_exists and not remote_exists:
            return self._handle_local_only(
                item_name, local_path, remote_path, is_dir, options, file_ops
            )
        elif not local_exists and remote_exists:
            return self._handle_remote_only(
                item_name, local_path, remote_path, is_dir, options, file_ops
            )
        else:
            return self._create_operation_result(
                item_name, "skip", True, "Item exists in neither location"
            )

    def _handle_conflict(
        self,
        item_name: str,
        local_path: Path,
        remote_path: Path,
        is_dir: bool,
        options: SyncOptions,
        file_ops,
    ) -> OperationResult:
        """Handle conflict when both local and remote exist."""
        if file_ops.paths_identical(local_path, remote_path, is_dir):
            return self._create_operation_result(
                item_name, "skip", True, "Files are identical"
            )

        if options.dry_run:
            return self._handle_dry_run_operation(
                item_name, "resolve_conflict", "resolve conflict"
            )

        if options.force:
            if options.conflict_resolution == ConflictResolution.LOCAL:
                console.print(f"[success]Using local version: {item_name}[/success]")
                file_ops.remove_path(remote_path, is_dir)
                file_ops.copy_path(local_path, remote_path, is_dir)
                return self._create_operation_result(
                    item_name, "use_local", True, "Used local version"
                )
            else:
                console.print(f"[success]Using remote version: {item_name}[/success]")
                file_ops.remove_path(local_path, is_dir)
                file_ops.copy_path(remote_path, local_path, is_dir)
                return self._create_operation_result(
                    item_name, "use_remote", True, "Used remote version"
                )
        else:
            # Interactive resolution
            choice = self._resolve_conflict_interactive(
                item_name, local_path, remote_path, file_ops
            )
            return self._create_operation_result(
                item_name, f"use_{choice}", True, f"Used {choice} version (interactive)"
            )

    def _handle_local_only(
        self,
        item_name: str,
        local_path: Path,
        remote_path: Path,
        is_dir: bool,
        options: SyncOptions,
        file_ops,
    ) -> OperationResult:
        """Handle case where item exists only locally."""
        if options.dry_run:
            return self._handle_dry_run_operation(
                item_name, "copy_to_repo", "copy to repo"
            )

        console.print(f"[success]Copying to repo: {item_name}[/success]")
        file_ops.copy_path(local_path, remote_path, is_dir)
        return self._create_operation_result(
            item_name, "copy_to_repo", True, "Copied to repo successfully"
        )

    def _handle_remote_only(
        self,
        item_name: str,
        local_path: Path,
        remote_path: Path,
        is_dir: bool,
        options: SyncOptions,
        file_ops,
    ) -> OperationResult:
        """Handle case where item exists only remotely."""
        if options.dry_run:
            return self._handle_dry_run_operation(
                item_name, "copy_to_local", "copy to local"
            )

        console.print(f"[success]Copying to local: {item_name}[/success]")
        file_ops.copy_path(remote_path, local_path, is_dir)
        return self._create_operation_result(
            item_name, "copy_to_local", True, "Copied to local successfully"
        )

    def _resolve_conflict_interactive(
        self, item_name: str, local_path: Path, remote_path: Path, file_ops
    ) -> str:
        """Resolve conflict interactively."""
        # For now, just prefer remote (will implement interactive resolution later)
        console.print(f"[warning]Conflict detected for: {item_name}[/warning]")
        console.print(
            "[info]Using remote version (interactive resolution not yet implemented)[/info]"
        )
        file_ops.remove_path(local_path, local_path.is_dir())
        file_ops.copy_path(remote_path, local_path, local_path.is_dir())
        return "remote"
