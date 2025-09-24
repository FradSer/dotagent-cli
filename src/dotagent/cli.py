"""Main CLI application using Typer."""

from typing import Optional
from collections import Counter

import typer
from rich.console import Console
from rich.table import Table

from dotagent import __version__
from dotagent.core.sync_engine import SyncEngine
from dotagent.domain.value_objects import ConflictResolution, SyncOptions
from dotagent.utils.console import create_console

console = Console()
rich_console = create_console()

app = typer.Typer(
    name="dotagent",
    help="Universal CLI tool for managing AI agent configurations across different platforms",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Claude subcommand
claude_app = typer.Typer(
    name="claude",
    help="Manage Claude Code configurations",
    rich_markup_mode="rich",
    no_args_is_help=True,
)
app.add_typer(claude_app, name="claude")

# Constants for operation display names
OPERATION_DISPLAY_NAMES = {
    "use_local": "used local version",
    "use_remote": "used remote version",
    "copy_to_repo": "copied to repo",
    "copy_to_local": "copied to local",
    "create": "created",
    "update": "updated",
    "skip": "skipped",
}


def version_callback(show_version: bool) -> None:
    """Show version information."""
    if show_version:
        console.print(
            f"[bold blue]dotagent[/bold blue] version [green]{__version__}[/green]"
        )
        raise typer.Exit()


def _determine_target_branch(branch: Optional[str]) -> str:
    """Determine the target branch.

    Args:
        branch: Explicit branch name if provided

    Returns:
        The target branch name
    """
    return branch or "main"


def _create_sync_options(
    dry_run: bool, force: bool, branch: Optional[str], repo_url: Optional[str], **kwargs
) -> SyncOptions:
    """Create SyncOptions with common parameter processing.

    Args:
        dry_run: Dry run flag
        force: Force flag
        branch: Explicit branch name
        repo_url: Repository URL
        **kwargs: Additional options for SyncOptions (including include_local_agents)

    Returns:
        Configured SyncOptions instance
    """
    target_branch = _determine_target_branch(branch)

    return SyncOptions(
        dry_run=dry_run,
        force=force,
        branch=target_branch,
        repository_url=repo_url,
        **kwargs,
    )


def _display_operation_summary(result) -> None:
    """Display summary of operations performed."""
    if not (hasattr(result, "operations") and result.operations):
        return

    operation_counts = Counter(op.operation for op in result.operations)
    summary_parts = [
        f"{count} {OPERATION_DISPLAY_NAMES.get(op_type, op_type)}"
        for op_type, count in operation_counts.items()
    ]

    if summary_parts:
        rich_console.print(f"[dim]Summary: {', '.join(summary_parts)}[/dim]")


def _handle_sync_result(result, operation_name: str) -> None:
    """Handle and display sync operation results.

    Args:
        result: The sync result object
        operation_name: Name of the operation for display
    """
    if result.success:
        rich_console.print(
            f"[bold green]{operation_name} completed successfully![/bold green]"
        )

        # Show operation type for bidirectional sync
        if hasattr(result, "operation_type") and result.operation_type:
            rich_console.print(f"Operation: {result.operation_type}")

        rich_console.print(f"Items processed: {result.items_processed}")
        rich_console.print(f"Duration: {result.duration:.2f}s")

        _display_operation_summary(result)

        # Display any failure warnings
        if result.has_failures:
            failure_summary = result.get_failure_summary()
            if failure_summary:
                rich_console.print(f"[yellow]Warning: {failure_summary}[/yellow]")
    else:
        rich_console.print(
            f"[bold red]{operation_name} failed: {result.error}[/bold red]"
        )
        raise typer.Exit(1)


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """
    [bold blue]dotagent[/bold blue] - Universal CLI for AI agent configuration management

    Manage agent configurations across different platforms and tools.

    Available tools:
    - claude: Manage Claude Code configurations
    """
    pass


@claude_app.command()
def sync(
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview changes without applying"
    ),
    force: bool = typer.Option(
        False, "--force", help="Force overwrite without prompts"
    ),
    branch: Optional[str] = typer.Option(None, "--branch", help="Use specific branch"),
    repo: Optional[str] = typer.Option(
        None,
        "--repo",
        help="Repository URL (supports HTTPS, SSH, or user/repo format)",
    ),
    include_local_agents: bool = typer.Option(
        False, "--local", help="Include project-specific agents in sync"
    ),
) -> None:
    """Sync configuration with repository."""
    rich_console.print("[bold blue]Starting bidirectional sync...[/bold blue]")

    # For interactive mode, we'll use PROMPT for conflict resolution when not forced
    conflict_resolution = (
        ConflictResolution.REMOTE if force else ConflictResolution.PROMPT
    )

    options = _create_sync_options(
        dry_run,
        force,
        branch,
        repo,
        conflict_resolution=conflict_resolution,
        include_local_agents=include_local_agents,
    )

    engine = SyncEngine()
    result = engine.sync(options)

    _handle_sync_result(result, "Sync")


@claude_app.command()
def status(
    branch: Optional[str] = typer.Option(None, "--branch", help="Use specific branch"),
    repo: Optional[str] = typer.Option(
        None,
        "--repo",
        help="Repository URL (supports HTTPS, SSH, or user/repo format)",
    ),
) -> None:
    """Show sync status and differences."""
    target_branch = _determine_target_branch(branch)
    rich_console.print(
        f"[bold blue]Checking sync status against {target_branch} branch...[/bold blue]"
    )

    options = _create_sync_options(
        dry_run=True,  # Always dry run for status
        force=False,
        branch=branch,
        repo_url=repo,
    )

    engine = SyncEngine()
    result = engine.sync(options)

    # Display sync status tables
    _display_sync_status_tables(result, target_branch)


def _get_item_sync_status(operation_type: str) -> tuple[str, str]:
    """Get status and color for an item based on operation type."""
    if operation_type == "skip":
        return "In sync", "green"
    elif operation_type == "resolve_conflict":
        return "Conflict", "yellow"
    elif operation_type == "copy_to_repo":
        return "Needs push", "red"
    elif operation_type == "copy_to_local":
        return "Needs pull", "red"
    else:
        return operation_type, "dim"


def _get_item_description(item_name: str) -> str:
    """Get description for sync item."""
    descriptions = {
        "agents": "Global AI agents",
        "commands": "Global commands",
        "CLAUDE.md": "Global configuration file",
        "local-agents": "Project-specific agents",
    }
    return descriptions.get(item_name, "Configuration item")


def _display_sync_status_tables(result, target_branch: str) -> None:
    """Display sync status tables separated by global and local configurations."""
    if not hasattr(result, "operations") or not result.operations:
        rich_console.print("[dim]No items found. Check repository configuration.[/dim]")
        return

    # Separate global and local items
    global_items = []
    local_items = []

    for operation in result.operations:
        item_name = (
            operation.item_name if hasattr(operation, "item_name") else "Unknown"
        )
        status_text, status_color = _get_item_sync_status(operation.operation)

        item_data = {
            "name": item_name,
            "status": f"[{status_color}]{status_text}[/{status_color}]",
            "description": _get_item_description(item_name),
        }

        if item_name == "local-agents":
            local_items.append(item_data)
        else:
            global_items.append(item_data)

    # Display global configuration status
    if global_items:
        rich_console.print(
            f"\n[bold blue]Global Configuration[/bold blue] [dim](from ~/.claude/)[/dim]"
        )
        global_table = Table(show_header=True, header_style="bold magenta", box=None)
        global_table.add_column("Item", style="cyan", no_wrap=True)
        global_table.add_column("Status", style="white")
        global_table.add_column("Description", style="dim")

        for item in global_items:
            global_table.add_row(item["name"], item["status"], item["description"])

        rich_console.print(global_table)

    # Display local configuration status
    if local_items:
        rich_console.print(
            f"\n[bold blue]Local Configuration[/bold blue] [dim](remote local-agents/ -> .claude/agents/)[/dim]"
        )
        local_table = Table(show_header=True, header_style="bold magenta", box=None)
        local_table.add_column("Item", style="cyan", no_wrap=True)
        local_table.add_column("Status", style="white")
        local_table.add_column("Description", style="dim")

        for item in local_items:
            local_table.add_row(item["name"], item["status"], item["description"])

        rich_console.print(local_table)

    # Show summary
    rich_console.print()
    _display_operation_summary(result)


if __name__ == "__main__":
    app()
