"""Core synchronization engine for dotclaude."""

from datetime import datetime

from rich.progress import Progress, SpinnerColumn, TextColumn

from dotclaude.core.git_manager import GitManager
from dotclaude.core.sync_strategies import (
    BidirectionalSyncStrategy,
    PullSyncStrategy,
    PushSyncStrategy,
)
from dotclaude.core.sync_utils import SyncContextManager
from dotclaude.domain.constants import DefaultPaths, DefaultRepository, SyncItems
from dotclaude.domain.value_objects import SyncOptions, SyncResult
from dotclaude.utils.console import console


class SyncEngine:
    """Main synchronization engine using Strategy pattern."""

    def __init__(self):
        self.git_manager = GitManager()
        self.repo_url = DefaultRepository.URL
        self.sync_items = SyncItems.ITEMS
        self.claude_dir = DefaultPaths.CLAUDE_DIR
        self.context_manager = SyncContextManager(
            self.git_manager, self.repo_url, self.claude_dir
        )

        # Initialize strategies
        self.strategies = {
            "pull": PullSyncStrategy(
                self.git_manager, self.sync_items, self.claude_dir
            ),
            "push": PushSyncStrategy(
                self.git_manager, self.sync_items, self.claude_dir
            ),
            "bidirectional": BidirectionalSyncStrategy(
                self.git_manager, self.sync_items, self.claude_dir
            ),
        }

    def sync(self, options: SyncOptions) -> SyncResult:
        """Execute synchronization based on options using Strategy pattern."""
        start_time = datetime.now()

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Initializing sync...", total=None)

                # Initialize sync context
                working_dir = self.context_manager.initialize_context(options.branch)
                progress.update(task, description="Sync context initialized")

                # Determine operation type and strategy
                operation_type, strategy = self._get_strategy(options)

                # Execute the strategy
                operations = strategy.execute(working_dir, options)

                end_time = datetime.now()

                result = SyncResult.create_success(
                    operation_type=operation_type,
                    start_time=start_time,
                    end_time=end_time,
                    operations=operations,
                    branch=options.branch,
                    dry_run=options.dry_run,
                )

                # Cleanup
                self.context_manager.cleanup_context(working_dir)

                return result

        except Exception as e:
            console.print(f"[error]Sync failed: {e}[/error]")
            end_time = datetime.now()
            return SyncResult.create_failure(
                operation_type="unknown",
                start_time=start_time,
                end_time=end_time,
                error=str(e),
                branch=getattr(options, "branch", "main"),
                dry_run=getattr(options, "dry_run", False),
            )

    def _get_strategy(self, options: SyncOptions) -> tuple[str, object]:
        """Get the appropriate strategy based on sync options."""
        if options.pull_only:
            return "pull", self.strategies["pull"]
        elif options.push_only:
            return "push", self.strategies["push"]
        else:
            return "bidirectional", self.strategies["bidirectional"]
