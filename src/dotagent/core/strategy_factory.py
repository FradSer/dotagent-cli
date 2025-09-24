"""Strategy Factory for creating sync strategies."""

from pathlib import Path

from dotagent.core.git_manager import GitManager
from dotagent.core.sync_strategies import (
    BidirectionalSyncStrategy,
    PullSyncStrategy,
    PushSyncStrategy,
    SyncStrategy,
)
from dotagent.domain.value_objects import SyncOptions


class StrategyFactory:
    """Factory for creating sync strategies based on options."""

    def __init__(self, git_manager: GitManager, sync_items: list, claude_dir: Path):
        """Initialize the strategy factory.

        Args:
            git_manager: Git operations manager
            sync_items: List of items to sync
            claude_dir: Claude configuration directory
        """
        self.git_manager = git_manager
        self.sync_items = sync_items
        self.claude_dir = claude_dir

        # Strategy registry
        self._strategies: dict[str, type[SyncStrategy]] = {
            "pull": PullSyncStrategy,
            "push": PushSyncStrategy,
            "bidirectional": BidirectionalSyncStrategy,
        }

    def create_strategy(self, options: SyncOptions) -> tuple[str, SyncStrategy]:
        """Create appropriate strategy based on sync options.

        Args:
            options: Sync configuration options

        Returns:
            Tuple of (operation_type, strategy_instance)

        Raises:
            ValueError: If no appropriate strategy found
        """
        operation_type = self._determine_operation_type(options)
        strategy_class = self._strategies.get(operation_type)

        if strategy_class is None:
            raise ValueError(f"Unknown operation type: {operation_type}")

        strategy = strategy_class(self.git_manager, self.sync_items, self.claude_dir)

        return operation_type, strategy

    def _determine_operation_type(self, options: SyncOptions) -> str:
        """Determine the operation type from sync options.

        Args:
            options: Sync configuration options

        Returns:
            Operation type string
        """
        if options.pull_only:
            return "pull"
        elif options.push_only:
            return "push"
        else:
            return "bidirectional"

    def register_strategy(
        self, operation_type: str, strategy_class: type[SyncStrategy]
    ) -> None:
        """Register a new strategy type.

        Args:
            operation_type: The operation type identifier
            strategy_class: The strategy class to register
        """
        self._strategies[operation_type] = strategy_class

    def get_available_strategies(self) -> list[str]:
        """Get list of available strategy types.

        Returns:
            List of available operation types
        """
        return list(self._strategies.keys())
