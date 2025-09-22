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

    # Create a status table
    table = Table(title=f"Sync Status - {target_branch} branch", show_header=True, header_style="bold magenta")
    table.add_column("Item", style="cyan", no_wrap=True)
    table.add_column("Local Status", style="green")
    table.add_column("Remote Status", style="yellow")
    table.add_column("Sync Status", style="white")

    if hasattr(result, 'operations') and result.operations:
        for operation in result.operations:
            item_name = operation.item_name if hasattr(operation, 'item_name') else "Unknown"

            # Determine status based on operation
            if operation.operation == "skip":
                local_status = "Present"
                remote_status = "Present"
                sync_status = "[green]In sync[/green]"
            elif operation.operation == "resolve_conflict":
                local_status = "Modified"
                remote_status = "Modified"
                sync_status = "[yellow]Conflict[/yellow]"
            elif operation.operation == "copy_to_repo":
                local_status = "Present"
                remote_status = "Missing"
                sync_status = "[red]Needs push[/red]"
            elif operation.operation == "copy_to_local":
                local_status = "Missing"
                remote_status = "Present"
                sync_status = "[red]Needs pull[/red]"
            else:
                local_status = "Unknown"
                remote_status = "Unknown"
                sync_status = f"[dim]{operation.operation}[/dim]"

            table.add_row(item_name, local_status, remote_status, sync_status)
    else:
        # Fallback if no operations data
        table.add_row("No items found", "N/A", "N/A", "[dim]Check repository configuration[/dim]")

    console.print(table)

    # Show summary
    if hasattr(result, 'operations') and result.operations:
        _display_operation_summary(result)


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
