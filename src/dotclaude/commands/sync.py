"""Sync command for managing repository synchronization."""

from typing import Optional

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


def _handle_sync_result(result, operation_name: str) -> None:
    """Handle and display sync operation results.

    Args:
        result: The sync result object
        operation_name: Name of the operation for display
    """
    if result.success:
        console.print(f"[bold green]{operation_name} completed successfully![/bold green]")

        # Show operation type for bidirectional sync
        if hasattr(result, 'operation_type') and result.operation_type:
            console.print(f"Operation: {result.operation_type}")

        console.print(f"Items processed: {result.items_processed}")
        console.print(f"Duration: {result.duration:.2f}s")

        if result.has_failures:
            failure_summary = result.get_failure_summary()
            if failure_summary:
                console.print(f"[yellow]Warning: {failure_summary}[/yellow]")
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

        # Fix parameter types from Typer parsing issues
        dry_run = bool(dry_run) if dry_run is not None else False
        force = bool(force) if force != 'False' else False
        develop = bool(develop) if develop != 'False' else False

        # Determine target branch using helper function
        target_branch = _determine_target_branch(develop, branch)

        options = SyncOptions(
            conflict_resolution=conflict_resolution,
            dry_run=dry_run,
            force=force,
            branch=target_branch,
            repository_url=repo_url,
        )

        engine = SyncEngine()
        result = engine.sync(options)

        _handle_sync_result(result, "Sync")


@app.command()
def status() -> None:
    """Show sync status and differences."""
    console.print("[bold blue]Checking sync status...[/bold blue]")

    # TODO: Implement status checking
    table = Table(title="Sync Status", show_header=True, header_style="bold magenta")
    table.add_column("Item", style="cyan", no_wrap=True)
    table.add_column("Local", style="green")
    table.add_column("Remote", style="yellow")
    table.add_column("Status", style="red")

    # Placeholder data
    table.add_row("agents/", "5 files", "5 files", "In sync")
    table.add_row("commands/", "18 files", "18 files", "In sync")
    table.add_row("CLAUDE.md", "Modified", "Original", "Needs sync")

    console.print(table)


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

    # Fix parameter types from Typer parsing issues
    dry_run = bool(dry_run) if dry_run is not None else False
    force = bool(force) if force != 'False' else False
    develop = bool(develop) if develop != 'False' else False

    # Determine target branch using helper function
    target_branch = _determine_target_branch(develop, branch)

    options = SyncOptions(
        pull_only=True, dry_run=dry_run, force=force, branch=target_branch, repository_url=repo_url
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

    # Fix parameter types from Typer parsing issues
    dry_run = bool(dry_run) if dry_run is not None else False
    force = bool(force) if force != 'False' else False
    develop = bool(develop) if develop != 'False' else False

    # Determine target branch using helper function
    target_branch = _determine_target_branch(develop, branch)

    options = SyncOptions(
        push_only=True, dry_run=dry_run, force=force, branch=target_branch, repository_url=repo_url
    )

    engine = SyncEngine()
    result = engine.sync(options)

    _handle_sync_result(result, "Push")


if __name__ == "__main__":
    app()
