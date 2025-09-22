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

        # Determine target branch
        if develop and branch:
            console.print("Cannot use both --develop and --branch options")
            raise typer.Exit(1)

        target_branch = "develop" if develop else (branch or "main")

        options = SyncOptions(
            conflict_resolution=conflict_resolution,
            dry_run=dry_run,
            force=force,
            branch=target_branch,
        )

        engine = SyncEngine()
        result = engine.sync(options)

        if result.success:
            console.print("[bold green]Sync completed successfully![/bold green]")
            console.print(f"Operation: {result.operation_type}")
            console.print(f"Items processed: {result.items_processed}")
            console.print(f"Duration: {result.duration:.2f}s")

            if result.has_failures:
                failure_summary = result.get_failure_summary()
                if failure_summary:
                    console.print(f"[yellow]Warning: {failure_summary}[/yellow]")
        else:
            console.print(f"[bold red]Sync failed: {result.error}[/bold red]")
            raise typer.Exit(1)


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
) -> None:
    """Pull changes from repository."""
    console.print("[bold green]Pulling from repository...[/bold green]")

    # Determine target branch
    if develop and branch:
        console.print("Cannot use both --develop and --branch options")
        raise typer.Exit(1)

    target_branch = "develop" if develop else (branch or "main")

    options = SyncOptions(
        pull_only=True, dry_run=dry_run, force=force, branch=target_branch
    )

    engine = SyncEngine()
    result = engine.sync(options)

    if result.success:
        console.print("[bold green]Pull completed successfully![/bold green]")
        console.print(f"Items processed: {result.items_processed}")
        console.print(f"Duration: {result.duration:.2f}s")

        if result.has_failures:
            failure_summary = result.get_failure_summary()
            if failure_summary:
                console.print(f"[yellow]Warning: {failure_summary}[/yellow]")
    else:
        console.print(f"[bold red]Pull failed: {result.error}[/bold red]")
        raise typer.Exit(1)


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
) -> None:
    """Push changes to repository."""
    console.print("[bold yellow]Pushing to repository...[/bold yellow]")

    # Determine target branch
    if develop and branch:
        console.print("Cannot use both --develop and --branch options")
        raise typer.Exit(1)

    target_branch = "develop" if develop else (branch or "main")

    options = SyncOptions(
        push_only=True, dry_run=dry_run, force=force, branch=target_branch
    )

    engine = SyncEngine()
    result = engine.sync(options)

    if result.success:
        console.print("[bold green]Push completed successfully![/bold green]")
        console.print(f"Items processed: {result.items_processed}")
        console.print(f"Duration: {result.duration:.2f}s")

        if result.has_failures:
            failure_summary = result.get_failure_summary()
            if failure_summary:
                console.print(f"[yellow]Warning: {failure_summary}[/yellow]")
    else:
        console.print(f"[bold red]Push failed: {result.error}[/bold red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
