"""Sync use case - contains core synchronization business logic."""

from datetime import datetime
from pathlib import Path

from dotagent.domain.constants import SyncItems
from dotagent.domain.interfaces import GitManagerInterface
from dotagent.domain.value_objects import SyncOptions, SyncResult

from .strategy_factory import StrategyFactory
from .sync_utils import SyncContextManager


class ConfigManagerInterface:
    """Interface defining configuration operations."""

    def get_effective_repository_url(self, repository_url: str | None) -> str:
        """Get the effective repository URL with proper precedence."""
        ...


class SyncUseCase:
    """Use case for synchronization operations.

    Contains the core business logic for sync operations, orchestrating
    the interaction between different domain services.
    """

    def __init__(
        self,
        git_manager: GitManagerInterface,
        config_manager: ConfigManagerInterface,
        claude_dir: Path
    ):
        self.git_manager = git_manager
        self.config_manager = config_manager
        self.sync_items = SyncItems.ITEMS
        self.claude_dir = claude_dir

    def execute(self, options: SyncOptions) -> SyncResult:
        """Execute synchronization based on options using Strategy pattern."""
        start_time = datetime.now()

        # Get effective repository URL with proper precedence
        repo_url = self.config_manager.get_effective_repository_url(
            options.repository_url
        )

        try:
            # Create context manager with the effective repository URL
            context_manager = SyncContextManager(
                self.git_manager, repo_url, self.claude_dir
            )

            # Initialize sync context
            working_dir = context_manager.initialize_context(options.branch)

            # Create strategy using factory pattern
            strategy_factory = StrategyFactory(
                self.git_manager, self.sync_items, self.claude_dir
            )
            operation_type, strategy = strategy_factory.create_strategy(options)

            # Execute the strategy
            operations = strategy.execute(working_dir, options)

            # Operations completed
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
