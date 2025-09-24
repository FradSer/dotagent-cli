"""Common utilities for command handling to reduce duplication."""

from functools import wraps
from typing import Any, Callable, Optional

import typer

from dotagent.core.config_manager import ConfigScope
from dotagent.infrastructure.services.console_service import RichConsoleService
from dotagent.utils.console import create_console

console = create_console()
console_service = RichConsoleService()


class ScopeValidator:
    """Validates and converts scope strings to ConfigScope enums."""

    @staticmethod
    def validate_scope(scope: str, allow_none: bool = False) -> Optional[ConfigScope]:
        """Validate scope string and return ConfigScope enum."""
        if scope is None:
            if allow_none:
                return None
            raise ValueError("Scope cannot be None")

        try:
            return ConfigScope(scope)
        except ValueError as e:
            console_service.print_error("Invalid scope. Use: local, global, or system")
            raise typer.Exit(1) from e


class ErrorHandler:
    """Handles common error patterns in commands."""

    @staticmethod
    def handle_config_error(func: Callable) -> Callable:
        """Decorator to handle configuration errors consistently."""

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                console.print(f"[red]Operation failed: {e}[/red]")
                raise typer.Exit(1) from e

        return wrapper

    @staticmethod
    def handle_scope_validation(scope: Optional[str]) -> Optional[ConfigScope]:
        """Handle scope validation with consistent error handling."""
        if scope is None:
            return None

        try:
            return ConfigScope(scope)
        except ValueError as e:
            console_service.print_error("Invalid scope. Use: local, global, or system")
            raise typer.Exit(1) from e


class OutputFormatter:
    """Consistent formatting for command outputs."""

    @staticmethod
    def success(message: str) -> None:
        """Display success message."""
        console_service.print_success(message)

    @staticmethod
    def error(message: str) -> None:
        """Display error message."""
        console_service.print_error(message)

    @staticmethod
    def info(message: str) -> None:
        """Display info message."""
        console.print(f"[blue]ⓘ[/blue] {message}")

    @staticmethod
    def warning(message: str) -> None:
        """Display warning message."""
        console_service.print_warning(message)

    @staticmethod
    def config_value(key: str, value: str, scope: Optional[str] = None) -> None:
        """Display configuration key-value pair."""
        scope_part = f" ([yellow]{scope}[/yellow])" if scope else ""
        console.print(f"[cyan]{key}[/cyan] = [green]{value}[/green]{scope_part}")


def with_config_manager(func: Callable) -> Callable:
    """Decorator to inject ConfigManager instance."""

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        from dotagent.core.config_manager import ConfigManager

        kwargs["manager"] = ConfigManager()
        return func(*args, **kwargs)

    return wrapper


def validate_scope(scope: Optional[str] = None, required: bool = False) -> Callable:
    """Decorator to validate scope parameter."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, scope: Optional[str] = scope, **kwargs) -> Any:
            if scope is None and required:
                console.print("[red]Scope is required for this operation[/red]")
                raise typer.Exit(1)

            if scope is not None:
                kwargs["scope_enum"] = ErrorHandler.handle_scope_validation(scope)
            else:
                kwargs["scope_enum"] = None

            return func(*args, **kwargs)

        return wrapper

    return decorator
