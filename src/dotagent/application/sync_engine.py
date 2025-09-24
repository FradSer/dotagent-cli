"""Application layer synchronization engine."""

from rich.progress import Progress, SpinnerColumn, TextColumn

from dotagent.application.config_manager import ConfigManager
from dotagent.application.git_manager import GitManager
from dotagent.domain.constants import DefaultPaths
from dotagent.domain.value_objects import SyncOptions, SyncResult
from dotagent.use_cases import SyncUseCase
from dotagent.utils.console import console


class SyncEngine:
    """Application layer orchestrator for sync operations."""

    def __init__(self):
        self.git_manager = GitManager()
        self.config_manager = ConfigManager()
        self.claude_dir = DefaultPaths.CLAUDE_DIR
        self.sync_use_case = SyncUseCase(
            self.git_manager,
            self.config_manager,
            self.claude_dir
        )

    def sync(self, options: SyncOptions) -> SyncResult:
        """Execute synchronization with progress indication."""
        try:
            # For non-interactive operations, use progress bar
            if options.force or options.dry_run:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Initializing sync...", total=None)
                    progress.update(task, description="Executing sync use case...")

                    result = self.sync_use_case.execute(options)

                    progress.update(task, description="Sync completed", completed=True)
                    return result
            else:
                # For interactive operations, don't use progress bar to avoid conflicts
                console.print("[blue]Initializing sync...[/blue]")
                result = self.sync_use_case.execute(options)
                return result

        except Exception as e:
            # Handle any unexpected errors at application layer
            console.print(f"[red]Sync failed: {e}[/red]")
            raise
