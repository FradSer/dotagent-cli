"""Configuration management commands."""

from typing import Optional

import typer
from rich.table import Table

from dotclaude.commands.command_utils import (
    ErrorHandler,
    OutputFormatter,
    validate_scope,
    with_config_manager,
)
from dotclaude.core.config_manager import ConfigManager, ConfigScope
from dotclaude.utils.console import create_console

console = create_console()

app = typer.Typer(
    name="config",
    help="Manage configuration settings",
    rich_markup_mode="rich",
)


@app.command()
@with_config_manager
@validate_scope()
def get(
    key: str = typer.Argument(..., help="Configuration key to retrieve"),
    scope: Optional[str] = typer.Option(
        None, "--scope", help="Configuration scope: local, global, system"
    ),
    manager = None,
    scope_enum = None,
) -> None:
    """Get configuration value."""
    value = manager.get(key, scope=scope_enum) if scope_enum else manager.get(key)

    if value is not None:
        OutputFormatter.config_value(key, str(value))
    else:
        OutputFormatter.error(f"Configuration key '{key}' not found")
        raise typer.Exit(1)


@app.command()
@with_config_manager
@validate_scope(required=True)
@ErrorHandler.handle_config_error
def set(
    key: str = typer.Argument(..., help="Configuration key to set"),
    value: str = typer.Argument(..., help="Configuration value"),
    scope: str = typer.Option(
        "global", "--scope", help="Configuration scope: local, global, system"
    ),
    manager = None,
    scope_enum = None,
) -> None:
    """Set configuration value."""
    manager.set(key, value, scope=scope_enum)
    OutputFormatter.config_value(key, value, scope)


@app.command()
@with_config_manager
@validate_scope(required=True)
@ErrorHandler.handle_config_error
def unset(
    key: str = typer.Argument(..., help="Configuration key to remove"),
    scope: str = typer.Option(
        "global", "--scope", help="Configuration scope: local, global, system"
    ),
    manager = None,
    scope_enum = None,
) -> None:
    """Remove configuration value."""
    manager.unset(key, scope=scope_enum)
    OutputFormatter.success(f"Removed {key} from {scope} config")


@app.command()
def list(
    scope: Optional[str] = typer.Option(
        None, "--scope", help="Configuration scope: local, global, system"
    ),
) -> None:
    """List all configuration values."""
    manager = ConfigManager()

    if scope:
        try:
            scope_enum = ConfigScope(scope)
            configs = {scope: manager.get_all(scope=scope_enum)}
            title = f"{scope.title()} Configuration"
        except ValueError:
            console.print("Invalid scope. Use: local, global, or system")
            raise typer.Exit(1)
    else:
        configs = manager.get_all_scopes()
        title = "All Configuration"

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Scope", style="yellow", no_wrap=True)
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    for scope_name, scope_config in configs.items():
        for key, value in scope_config.items():
            table.add_row(scope_name, key, str(value))

    console.print(table)


@app.command()
def edit(
    scope: str = typer.Option(
        "global", "--scope", help="Configuration scope to edit: local, global, system"
    ),
) -> None:
    """Edit configuration file in default editor."""
    try:
        scope_enum = ConfigScope(scope)
    except ValueError:
        console.print("Invalid scope. Use: local, global, or system")
        raise typer.Exit(1)

    manager = ConfigManager()

    try:
        config_path = manager.get_config_path(scope_enum)
        console.print(f"Opening {scope} config: [yellow]{config_path}[/yellow]")
        manager.edit_config(scope_enum)
    except Exception as e:
        console.print(f"Failed to edit configuration: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
