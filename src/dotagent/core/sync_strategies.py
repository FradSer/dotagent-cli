"""Sync strategy implementations for different operation types."""

import os
from abc import ABC, abstractmethod
from pathlib import Path

from dotagent.core.git_manager import GitManager
from dotagent.domain.constants import Git
from dotagent.domain.value_objects import ConflictResolution, SyncOptions
from dotagent.domain.value_objects.sync_result import OperationResult, OperationStatus
from dotagent.infrastructure.services.interactive_service import InteractiveSyncService
from dotagent.utils.console import console


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

    def _execute_file_operation(
        self,
        item_name: str,
        source_path: Path,
        dest_path: Path,
        is_dir: bool,
        operation_type: str,
        options: SyncOptions,
    ) -> OperationResult:
        """Execute a file operation (create or update) with unified logic."""
        from dotagent.core.sync_utils import SyncFileOperations

        file_ops = SyncFileOperations()

        if not dest_path.exists():
            return self._handle_create_operation(
                item_name,
                source_path,
                dest_path,
                is_dir,
                operation_type,
                options,
                file_ops,
            )
        elif not file_ops.paths_identical(source_path, dest_path, is_dir):
            return self._handle_update_operation(
                item_name,
                source_path,
                dest_path,
                is_dir,
                operation_type,
                options,
                file_ops,
            )

        # No changes needed
        return self._create_operation_result(
            item_name, "skip", True, "No changes needed"
        )

    def _handle_create_operation(
        self,
        item_name: str,
        source_path: Path,
        dest_path: Path,
        is_dir: bool,
        operation_type: str,
        options: SyncOptions,
        file_ops,
    ) -> OperationResult:
        """Handle file creation operation."""
        if options.dry_run:
            return self._handle_dry_run_operation(
                item_name, "create", f"create {operation_type}"
            )

        console.print(f"[success]Creating {operation_type}: {item_name}[/success]")
        file_ops.copy_path(source_path, dest_path, is_dir)
        return self._create_operation_result(
            item_name, "create", True, f"Created {operation_type} successfully"
        )

    def _handle_update_operation(
        self,
        item_name: str,
        source_path: Path,
        dest_path: Path,
        is_dir: bool,
        operation_type: str,
        options: SyncOptions,
        file_ops,
    ) -> OperationResult:
        """Handle file update operation."""
        if options.dry_run:
            return self._handle_dry_run_operation(
                item_name, "update", f"update {operation_type}"
            )

        if options.force or self._prompt_overwrite(f"{item_name} {operation_type}"):
            console.print(f"[success]Updating {operation_type}: {item_name}[/success]")
            file_ops.remove_path(dest_path, is_dir)
            file_ops.copy_path(source_path, dest_path, is_dir)
            return self._create_operation_result(
                item_name, "update", True, f"Updated {operation_type} successfully"
            )
        else:
            console.print(f"[info]Skipping: {item_name}[/info]")
            return self._create_operation_result(
                item_name, "skip", True, "Skipped by user choice"
            )

    def _prompt_overwrite(self, item_name: str) -> bool:
        """Prompt user for overwrite confirmation."""
        # For now, just return True (will implement interactive prompts later)
        return True

    def _filter_sync_items(self, options: SyncOptions) -> list[tuple[str, str]]:
        """Filter sync items based on options."""
        filtered_items = []

        # Always include global items
        for item_name, item_type in self.sync_items:
            if item_name != "local-agents":
                filtered_items.append((item_name, item_type))

        # Only include local-agents if explicitly enabled
        if options.include_local_agents:
            for item_name, item_type in self.sync_items:
                if item_name == "local-agents":
                    filtered_items.append((item_name, item_type))
                    break

        return filtered_items

    def _process_local_agents_item(
        self, working_dir: Path, options: SyncOptions
    ) -> OperationResult:
        """Process local-agents item: remote/local-agents/ -> .claude/agents/ with file selection"""
        from dotagent.infrastructure.services.local_agents_service import (
            LocalAgentsService,
        )

        remote_local_agents = working_dir / "local-agents"
        project_agents = Path.cwd() / ".claude" / "agents"

        if not remote_local_agents.exists():
            return self._create_operation_result(
                "local-agents", "skip", True, "No local-agents in remote repository"
            )

        # Find .md files in remote local-agents
        md_files = list(remote_local_agents.glob("*.md"))
        if not md_files:
            return self._create_operation_result(
                "local-agents",
                "skip",
                True,
                "No .md files found in remote local-agents",
            )

        if options.dry_run:
            return self._handle_dry_run_operation(
                "local-agents",
                "copy_to_local",
                f"would process {len(md_files)} agent files",
            )

        # Use LocalAgentsService for file selection
        agents_service = LocalAgentsService()
        selected_files = agents_service.select_agent_files(
            remote_local_agents, options.force
        )

        if not selected_files:
            return self._create_operation_result(
                "local-agents", "skip", True, "No agent files selected"
            )

        # Copy selected files
        copied_count = agents_service.copy_selected_files(
            remote_local_agents, project_agents, selected_files
        )

        if copied_count > 0:
            return self._create_operation_result(
                "local-agents",
                "copy_to_local",
                True,
                f"Copied {copied_count} agent file(s)",
            )
        else:
            return self._create_operation_result(
                "local-agents", "skip", True, "No files were copied"
            )


class PullSyncStrategy(SyncStrategy):
    """Strategy for pull-only synchronization."""

    def execute(self, working_dir: Path, options: SyncOptions) -> list[OperationResult]:
        """Pull changes from repository to local."""
        console.print("[info]Pulling changes from repository...[/info]")
        operations = []

        # Ensure ~/.claude directory exists
        self.claude_dir.mkdir(exist_ok=True)

        # Filter sync items based on options
        filtered_items = self._filter_sync_items(options)

        for item_name, item_type in filtered_items:
            result = self._process_pull_item(working_dir, item_name, item_type, options)
            operations.append(result)

        return operations

    def _process_pull_item(
        self, working_dir: Path, item_name: str, item_type: str, options: SyncOptions
    ) -> OperationResult:
        """Process a single item for pull operation."""
        # Special handling for local-agents: remote/local-agents/ -> .claude/agents/
        if item_name == "local-agents":
            return self._process_local_agents_item(working_dir, options)

        remote_path = working_dir / item_name
        local_path = self.claude_dir / item_name

        if not remote_path.exists():
            return self._handle_missing_item(item_name, "in repository")

        is_dir = item_type == "dir"
        return self._execute_file_operation(
            item_name, remote_path, local_path, is_dir, "locally", options
        )


class PushSyncStrategy(SyncStrategy):
    """Strategy for push-only synchronization."""

    def execute(self, working_dir: Path, options: SyncOptions) -> list[OperationResult]:
        """Push changes from local to repository."""
        console.print("[info]Pushing changes to repository...[/info]")
        operations = []
        changes_made = 0

        os.chdir(working_dir)

        # Filter sync items based on options
        filtered_items = self._filter_sync_items(options)

        for item_name, item_type in filtered_items:
            result = self._process_push_item(working_dir, item_name, item_type, options)
            operations.append(result)
            if result.status == OperationStatus.SUCCESS and result.operation in [
                "create",
                "update",
            ]:
                changes_made += 1

        # Commit and push changes if there are any
        if changes_made > 0 and not options.dry_run:
            console.print(
                f"[info]Pushing {changes_made} changes to remote repository...[/info]"
            )
            try:
                self.git_manager.stage_all_changes()
                self.git_manager.create_commit(Git.COMMIT_MESSAGES["sync"])
                self.git_manager.push_changes(options.branch)
                console.print(
                    "[success]Successfully pushed changes to remote repository[/success]"
                )
            except Exception as e:
                console.print(f"[warning]Git operations failed: {e}[/warning]")
                console.print(
                    "[info]Local changes have been made but not pushed to remote[/info]"
                )

        return operations

    def _process_push_item(
        self, working_dir: Path, item_name: str, item_type: str, options: SyncOptions
    ) -> OperationResult:
        """Process a single item for push operation."""
        local_path = self.claude_dir / item_name
        remote_path = working_dir / item_name

        if not local_path.exists():
            return self._handle_missing_item(item_name, "locally")

        is_dir = item_type == "dir"
        return self._execute_file_operation(
            item_name, local_path, remote_path, is_dir, "in repo", options
        )


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

        # Filter sync items based on options
        filtered_items = self._filter_sync_items(options)

        for item_name, item_type in filtered_items:
            result = self._process_bidirectional_item(
                working_dir, item_name, item_type, options
            )
            operations.append(result)
            if result.status == OperationStatus.SUCCESS and result.operation in [
                "use_local",
                "copy_to_repo",
            ]:
                changes_made += 1

        # Commit and push if there are changes that need to be pushed to remote
        if changes_made > 0 and not options.dry_run:
            console.print(
                f"[info]Pushing {changes_made} changes to remote repository...[/info]"
            )
            try:
                self.git_manager.stage_all_changes()
                self.git_manager.create_commit(Git.COMMIT_MESSAGES["bidirectional"])
                self.git_manager.push_changes(options.branch)
                console.print(
                    "[success]Successfully pushed changes to remote repository[/success]"
                )
            except Exception as e:
                console.print(f"[warning]Git operations failed: {e}[/warning]")
                console.print(
                    "[info]Local changes have been made but not pushed to remote[/info]"
                )

        return operations

    def _process_bidirectional_item(
        self, working_dir: Path, item_name: str, item_type: str, options: SyncOptions
    ) -> OperationResult:
        """Process a single item for bidirectional operation."""
        from dotagent.core.sync_utils import SyncFileOperations

        # Special handling for local-agents: remote/local-agents/ -> .claude/agents/
        if item_name == "local-agents":
            return self._process_local_agents_item(working_dir, options)

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
            preference = (
                "local"
                if options.conflict_resolution == ConflictResolution.LOCAL
                else "remote"
            )
            return self._handle_dry_run_operation(
                item_name,
                "resolve_conflict",
                f"resolve conflict (would use {preference} version)",
            )

        if options.force:
            return self._resolve_conflict_forced(
                item_name, local_path, remote_path, is_dir, options, file_ops
            )
        else:
            # Interactive resolution
            choice = self._resolve_conflict_interactive(
                item_name, local_path, remote_path, is_dir, file_ops
            )
            if choice == "skip":
                return self._create_operation_result(
                    item_name, "skip", True, "Skipped by user choice (interactive)"
                )
            else:
                return self._create_operation_result(
                    item_name,
                    f"use_{choice}",
                    True,
                    f"Used {choice} version (interactive)",
                )

    def _resolve_conflict_forced(
        self,
        item_name: str,
        local_path: Path,
        remote_path: Path,
        is_dir: bool,
        options: SyncOptions,
        file_ops,
    ) -> OperationResult:
        """Resolve conflict using forced resolution strategy."""
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

    def _display_conflict_info(
        self, item_name: str, local_path: Path, remote_path: Path, is_dir: bool
    ) -> None:
        """Display conflict information to the user."""
        console.print(
            f"\n[bold yellow]WARNING: Conflict detected for: {item_name}[/bold yellow]"
        )
        console.print("Both local and remote versions exist and are different.")

        if is_dir:
            console.print(f"Local directory: {local_path}")
            console.print(f"Remote directory: {remote_path}")
        else:
            console.print(f"Local file: {local_path}")
            console.print(f"Remote file: {remote_path}")

    def _prompt_user_choice(self, item_name: str) -> int:
        """Prompt user for conflict resolution choice."""
        import inquirer

        choices = [
            "Use Local version (keep your changes)",
            "Use Remote version (use repository version)",
            "Skip this item (leave both unchanged)",
        ]

        try:
            questions = [
                inquirer.List(
                    "action",
                    message=f"Choose action for {item_name}",
                    choices=choices,
                    default=choices[0],
                ),
            ]
            answers = inquirer.prompt(questions)

            if answers is None:  # User pressed Ctrl+C
                return -1  # Signal interruption

            return choices.index(answers["action"])

        except (EOFError, KeyboardInterrupt):
            return -1  # Signal interruption

    def _execute_conflict_resolution(
        self,
        choice_index: int,
        item_name: str,
        local_path: Path,
        remote_path: Path,
        is_dir: bool,
        file_ops,
    ) -> str:
        """Execute the chosen conflict resolution action."""
        if choice_index == -1:  # Interrupted
            console.print(f"\n[yellow]Interrupted. Skipping {item_name}[/yellow]")
            return "skip"
        elif choice_index == 0:  # Use Local
            console.print(f"[green]Using local version of {item_name}[/green]")
            file_ops.remove_path(remote_path, is_dir)
            file_ops.copy_path(local_path, remote_path, is_dir)
            return "local"
        elif choice_index == 1:  # Use Remote
            console.print(f"[blue]Using remote version of {item_name}[/blue]")
            file_ops.remove_path(local_path, is_dir)
            file_ops.copy_path(remote_path, local_path, is_dir)
            return "remote"
        else:  # Skip
            console.print(f"[yellow]Skipping {item_name}[/yellow]")
            return "skip"

    def _resolve_conflict_interactive(
        self,
        item_name: str,
        local_path: Path,
        remote_path: Path,
        is_dir: bool,
        file_ops,
    ) -> str:
        """Resolve conflict interactively with arrow key support."""
        self._display_conflict_info(item_name, local_path, remote_path, is_dir)
        choice_index = self._prompt_user_choice(item_name)
        return self._execute_conflict_resolution(
            choice_index, item_name, local_path, remote_path, is_dir, file_ops
        )
