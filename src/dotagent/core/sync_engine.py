"""Core synchronization engine for dotclaude."""

from datetime import datetime

from rich.progress import Progress, SpinnerColumn, TextColumn

from dotagent.core.config_manager import ConfigManager
from dotagent.core.git_manager import GitManager
from dotagent.core.strategy_factory import StrategyFactory
from dotagent.core.sync_utils import SyncContextManager
from dotagent.domain.constants import DefaultPaths, SyncItems
from dotagent.domain.value_objects import SyncOptions, SyncResult
from dotagent.utils.console import console


class SyncEngine:
    """Main synchronization engine using Strategy pattern."""

    def __init__(self):
        self.git_manager = GitManager()
        self.config_manager = ConfigManager()
        self.sync_items = SyncItems.ITEMS
        self.claude_dir = DefaultPaths.CLAUDE_DIR

    def sync(self, options: SyncOptions) -> SyncResult:
        """Execute synchronization based on options using Strategy pattern."""
        start_time = datetime.now()

        # Get effective repository URL with proper precedence
        repo_url = self.config_manager.get_effective_repository_url(
            options.repository_url
        )

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Initializing sync...", total=None)

                # Create context manager with the effective repository URL
                context_manager = SyncContextManager(
                    self.git_manager, repo_url, self.claude_dir
                )

                # Initialize sync context
                working_dir = context_manager.initialize_context(options.branch)
                progress.update(task, description="Sync context initialized")

                # Create strategy using factory pattern
                strategy_factory = StrategyFactory(
                    self.git_manager, self.sync_items, self.claude_dir
                )
                operation_type, strategy = strategy_factory.create_strategy(options)
                progress.update(
                    task, description="Strategy initialized", completed=True
                )

            # Execute the strategy outside progress context for interactive prompts
            operations = strategy.execute(working_dir, options)

            # Operations completed, outside progress context
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
            context_manager.cleanup_context(working_dir)

            return result

        except Exception as e:
            end_time = datetime.now()
            return SyncResult.create_failure(
                operation_type="unknown",
                start_time=start_time,
                end_time=end_time,
                error=str(e),
                branch=getattr(options, "branch", "main"),
                dry_run=getattr(options, "dry_run", False),
            )
