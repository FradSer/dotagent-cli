"""Sync command for managing repository synchronization."""

from typing import Optional
from collections import Counter

import typer
from rich.table import Table

from dotclaude.core.sync_engine import SyncEngine
from dotclaude.domain.value_objects import ConflictResolution, SyncOptions
from dotclaude.utils.console import create_console

console = create_console()

app = typer.Typer(
    name="sync",
    help="Sync configuration with repository",
    rich_markup_mode="rich",
    no_args_is_help=False,  # Allow default behavior
)

# Constants for operation display names
OPERATION_DISPLAY_NAMES = {
    "use_local": "used local version",
    "use_remote": "used remote version",
    "copy_to_repo": "copied to repo",
    "copy_to_local": "copied to local",
    "create": "created",
    "update": "updated",
    "skip": "skipped"
}


def _fix_typer_parameters(dry_run: bool, force: bool, develop: bool) -> tuple[bool, bool, bool]:
    """Fix parameter types from Typer parsing issues.

    Args:
        dry_run: Raw dry_run parameter
        force: Raw force parameter
        develop: Raw develop parameter

    Returns:
        Tuple of fixed boolean parameters
    """
    return (
        bool(dry_run) if dry_run is not None else False,
        bool(force) if force != 'False' else False,
        bool(develop) if develop != 'False' else False
    )


def _create_sync_options(
    dry_run: bool,
    force: bool,
    develop: bool,
    branch: Optional[str],
    repo_url: Optional[str],
    **kwargs
) -> SyncOptions:
    """Create SyncOptions with common parameter processing.

    Args:
        dry_run: Dry run flag
        force: Force flag
        develop: Develop branch flag
        branch: Explicit branch name
        repo_url: Repository URL
        **kwargs: Additional options for SyncOptions

    Returns:
        Configured SyncOptions instance
    """
    fixed_dry_run, fixed_force, fixed_develop = _fix_typer_parameters(dry_run, force, develop)
    target_branch = _determine_target_branch(fixed_develop, branch)

    return SyncOptions(
        dry_run=fixed_dry_run,
        force=fixed_force,
        branch=target_branch,
        repository_url=repo_url,
        **kwargs
    )


def _determine_target_branch(develop: bool, branch: Optional[str]) -> str:
    """Determine the target branch from develop flag and branch option.

    Args:
        develop: Whether the develop flag is set
        branch: Explicit branch name if provided

    Returns:
        The target branch name

    Raises:
        typer.Exit: If both develop and branch options are provided
    """
    if develop and branch:
        console.print("Cannot use both --develop and --branch options")
        raise typer.Exit(1)

    return "develop" if develop else (branch or "main")


def _display_success_result(result, operation_name: str) -> None:
    """Display basic success information."""
    console.print(f"[bold green]{operation_name} completed successfully![/bold green]")

    # Show operation type for bidirectional sync
    if hasattr(result, 'operation_type') and result.operation_type:
        console.print(f"Operation: {result.operation_type}")

    console.print(f"Items processed: {result.items_processed}")
    console.print(f"Duration: {result.duration:.2f}s")


def _display_operation_summary(result) -> None:
    """Display summary of operations performed."""
    if not (hasattr(result, 'operations') and result.operations):
        return

    operation_counts = Counter(op.operation for op in result.operations)
    summary_parts = [
        f"{count} {OPERATION_DISPLAY_NAMES.get(op_type, op_type)}"
        for op_type, count in operation_counts.items()
    ]

    if summary_parts:
        console.print(f"[dim]Summary: {', '.join(summary_parts)}[/dim]")


def _display_failure_warnings(result) -> None:
    """Display any failure warnings."""
    if result.has_failures:
        failure_summary = result.get_failure_summary()
        if failure_summary:
            console.print(f"[yellow]Warning: {failure_summary}[/yellow]")


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


def _display_sync_status_tables(result, target_branch: str) -> None:
    """Display sync status tables separated by global and local configurations."""
    if not hasattr(result, 'operations') or not result.operations:
        console.print("[dim]No items found. Check repository configuration.[/dim]")
        return

    # Separate global and local items
    global_items = []
    local_items = []

    for operation in result.operations:
        item_name = operation.item_name if hasattr(operation, 'item_name') else "Unknown"
        status_text, status_color = _get_item_sync_status(operation.operation)

        item_data = {
            "name": item_name,
            "status": f"[{status_color}]{status_text}[/{status_color}]",
            "description": _get_item_description(item_name)
        }

        if item_name == "local-agents":
            local_items.append(item_data)
        else:
            global_items.append(item_data)

    # Display global configuration status
    if global_items:
        console.print(f"\n[bold blue]Global Configuration[/bold blue] [dim](from ~/.claude/)[/dim]")
        global_table = Table(show_header=True, header_style="bold magenta", box=None)
        global_table.add_column("Item", style="cyan", no_wrap=True)
        global_table.add_column("Status", style="white")
        global_table.add_column("Description", style="dim")

        for item in global_items:
            global_table.add_row(item["name"], item["status"], item["description"])

        console.print(global_table)

    # Display local configuration status
    if local_items:
        console.print(f"\n[bold blue]Local Configuration[/bold blue] [dim](remote local-agents/ -> .claude/agents/)[/dim]")
        local_table = Table(show_header=True, header_style="bold magenta", box=None)
        local_table.add_column("Item", style="cyan", no_wrap=True)
        local_table.add_column("Status", style="white")
        local_table.add_column("Description", style="dim")

        for item in local_items:
            local_table.add_row(item["name"], item["status"], item["description"])

        console.print(local_table)

    # Show summary
    console.print()
    _display_operation_summary(result)


def _get_item_description(item_name: str) -> str:
    """Get description for sync item."""
    descriptions = {
        "agents": "Global AI agents",
        "commands": "Global commands",
        "CLAUDE.md": "Global configuration file",
        "local-agents": "Project-specific agents"
    }
    return descriptions.get(item_name, "Configuration item")


def _handle_sync_result(result, operation_name: str) -> None:
    """Handle and display sync operation results.

    Args:
        result: The sync result object
        operation_name: Name of the operation for display
    """
    if result.success:
        _display_success_result(result, operation_name)
        _display_operation_summary(result)
        _display_failure_warnings(result)
    else:
        console.print(f"[bold red]{operation_name} failed: {result.error}[/bold red]")
        raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def sync_default(
    ctx: typer.Context,
    prefer: Optional[str] = typer.Option(
        "remote", "--prefer", help="Conflict resolution preference: local or remote"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview changes without applying"
    ),
    force: bool = typer.Option(
        False, "--force", help="Force overwrite without prompts"
    ),
    branch: Optional[str] = typer.Option(None, "--branch", help="Use specific branch"),
    develop: bool = typer.Option(
        False,
        "--develop",
        "-d",
        help="Use develop branch (shortcut for --branch develop)",
    ),
    repo_url: Optional[str] = typer.Option(
        None,
        "--repo-url",
        "--repo",
        help="Repository URL (supports HTTPS, SSH, or user/repo format)",
    ),
) -> None:
    """
    Sync configuration with repository.

    Runs bidirectional sync by default. Use subcommands for specific operations.
    """
    if ctx.invoked_subcommand is None:
        # Run default bidirectional sync
        console.print("[bold blue]Starting bidirectional sync...[/bold blue]")

        # Convert prefer to ConflictResolution
        conflict_resolution = (
            ConflictResolution.LOCAL if prefer == "local" else ConflictResolution.REMOTE
        )

        options = _create_sync_options(
            dry_run, force, develop, branch, repo_url,
            conflict_resolution=conflict_resolution
        )

        engine = SyncEngine()
        result = engine.sync(options)

        _handle_sync_result(result, "Sync")


@app.command()
def status(
    branch: Optional[str] = typer.Option(None, "--branch", help="Use specific branch"),
    develop: bool = typer.Option(
        False,
        "--develop",
        "-d",
        help="Use develop branch (shortcut for --branch develop)",
    ),
    repo_url: Optional[str] = typer.Option(
        None,
        "--repo-url",
        "--repo",
        help="Repository URL (supports HTTPS, SSH, or user/repo format)",
    ),
) -> None:
    """Show sync status and differences."""
    # Determine target branch using helper function
    fixed_dry_run, fixed_force, fixed_develop = _fix_typer_parameters(False, False, develop)
    target_branch = _determine_target_branch(fixed_develop, branch)

    console.print(f"[bold blue]Checking sync status against {target_branch} branch...[/bold blue]")

    options = _create_sync_options(
        dry_run=True,  # Always dry run for status
        force=False,
        develop=develop,
        branch=branch,
        repo_url=repo_url
    )

    engine = SyncEngine()
    result = engine.sync(options)

    # Create separate tables for global and local configurations
    _display_sync_status_tables(result, target_branch)


@app.command()
def pull(
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview changes without applying"
    ),
    force: bool = typer.Option(
        False, "--force", help="Force overwrite without prompts"
    ),
    branch: Optional[str] = typer.Option(None, "--branch", help="Use specific branch"),
    develop: bool = typer.Option(
        False,
        "--develop",
        "-d",
        help="Use develop branch (shortcut for --branch develop)",
    ),
    repo_url: Optional[str] = typer.Option(
        None,
        "--repo-url",
        "--repo",
        help="Repository URL (supports HTTPS, SSH, or user/repo format)",
    ),
) -> None:
    """Pull changes from repository."""
    console.print("[bold green]Pulling from repository...[/bold green]")

    options = _create_sync_options(
        dry_run, force, develop, branch, repo_url,
        pull_only=True
    )

    engine = SyncEngine()
    result = engine.sync(options)

    _handle_sync_result(result, "Pull")


@app.command()
def push(
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview changes without applying"
    ),
    force: bool = typer.Option(
        False, "--force", help="Force overwrite without prompts"
    ),
    branch: Optional[str] = typer.Option(None, "--branch", help="Use specific branch"),
    develop: bool = typer.Option(
        False,
        "--develop",
        "-d",
        help="Use develop branch (shortcut for --branch develop)",
    ),
    repo_url: Optional[str] = typer.Option(
        None,
        "--repo-url",
        "--repo",
        help="Repository URL (supports HTTPS, SSH, or user/repo format)",
    ),
) -> None:
    """Push changes to repository."""
    console.print("[bold yellow]Pushing to repository...[/bold yellow]")

    options = _create_sync_options(
        dry_run, force, develop, branch, repo_url,
        push_only=True
    )

    engine = SyncEngine()
    result = engine.sync(options)

    _handle_sync_result(result, "Push")


if __name__ == "__main__":
    app()
