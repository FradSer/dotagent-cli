"""Main CLI application using Typer."""

from typing import Optional

import typer
from rich.console import Console

from dotclaude import __version__
from dotclaude.commands import agent, config, sync

console = Console()

app = typer.Typer(
    name="dotclaude",
    help="Modern CLI tool for managing Claude Code configuration",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Add subcommands
app.add_typer(sync.app, name="sync", help="Sync configuration with repository")
app.add_typer(agent.app, name="agent", help="Manage AI agents")
app.add_typer(config.app, name="config", help="Manage configuration settings")


def version_callback(show_version: bool) -> None:
    """Show version information."""
    if show_version:
        console.print(
            f"[bold blue]dotclaude[/bold blue] version [green]{__version__}[/green]"
        )
        raise typer.Exit()


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
    [bold blue]dotclaude[/bold blue] - Modern CLI for Claude Code configuration management

    Sync agents, commands, and settings between local and remote repositories.
    """
    pass


if __name__ == "__main__":
    app()
