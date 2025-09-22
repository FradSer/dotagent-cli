"""Rich console utilities."""

from rich.console import Console
from rich.theme import Theme


def create_console() -> Console:
    """Create a configured Rich console with custom theme."""
    custom_theme = Theme(
        {
            "info": "cyan",
            "warning": "yellow",
            "error": "bold red",
            "success": "bold green",
            "highlight": "bold blue",
        }
    )

    return Console(theme=custom_theme, markup=True)


# Global console instance
console = create_console()
