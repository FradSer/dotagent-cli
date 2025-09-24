"""Console service implementation using Rich."""

from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from ...interfaces.services import ConsoleService


class RichConsoleService(ConsoleService):
    """Implementation of console service using Rich library."""

    def __init__(self) -> None:
        """Initialize Rich console service."""
        self._console = Console()

    def print(self, message: str, style: Optional[str] = None) -> None:
        """Print a message to the console."""
        self._console.print(message, style=style)

    def print_error(self, message: str) -> None:
        """Print an error message to the console."""
        self._console.print(f"[bold red]Error:[/bold red] {message}")

    def print_warning(self, message: str) -> None:
        """Print a warning message to the console."""
        self._console.print(f"[bold yellow]Warning:[/bold yellow] {message}")

    def print_success(self, message: str) -> None:
        """Print a success message to the console."""
        self._console.print(f"[bold green]Success:[/bold green] {message}")

    def print_table(
        self, data: list[dict[str, Any]], title: Optional[str] = None
    ) -> None:
        """Print data in a table format."""
        if not data:
            self.print("No data to display")
            return

        # Create table with headers from first row
        headers = list(data[0].keys())
        table = Table(title=title, show_header=True, header_style="bold magenta")

        for header in headers:
            table.add_column(header, style="cyan", no_wrap=True)

        # Add rows
        for row in data:
            table.add_row(*[str(row.get(header, "")) for header in headers])

        self._console.print(table)

    def confirm(self, message: str, default: bool = False) -> bool:
        """Ask for user confirmation."""
        try:
            return Confirm.ask(message, default=default, console=self._console)
        except KeyboardInterrupt:
            self.print_warning("Operation cancelled by user")
            return False

    def prompt(self, message: str, default: Optional[str] = None) -> str:
        """Prompt user for input."""
        try:
            return Prompt.ask(message, default=default, console=self._console)
        except KeyboardInterrupt:
            self.print_warning("Operation cancelled by user")
            return default or ""

    def select(self, message: str, choices: list[str]) -> str:
        """Let user select from a list of choices."""
        if not choices:
            raise ValueError("Choices list cannot be empty")

        if len(choices) == 1:
            return choices[0]

        self.print(f"\n{message}")
        for i, choice in enumerate(choices, 1):
            self.print(f"  {i}. {choice}")

        while True:
            try:
                response = self.prompt(f"Select option (1-{len(choices)})", default="1")

                if response.isdigit():
                    index = int(response) - 1
                    if 0 <= index < len(choices):
                        return choices[index]

                # Try to match by text
                for choice in choices:
                    if response.lower() in choice.lower():
                        return choice

                self.print_error(
                    f"Invalid selection. Please enter a number between 1 and {len(choices)}"
                )

            except KeyboardInterrupt:
                self.print_warning("Operation cancelled by user")
                return choices[0]  # Return first choice as default

    def print_panel(
        self, message: str, title: Optional[str] = None, style: Optional[str] = None
    ) -> None:
        """Print a message in a panel."""
        panel = Panel(message, title=title, border_style=style or "blue")
        self._console.print(panel)

    def print_progress(self, message: str, current: int, total: int) -> None:
        """Print progress information."""
        percentage = (current / total * 100) if total > 0 else 0
        progress_bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
        self.print(f"{message} [{progress_bar}] {current}/{total} ({percentage:.1f}%)")

    def print_status(self, message: str, status: str) -> None:
        """Print a status message with colored indicator."""
        status_colors = {
            "success": "green",
            "error": "red",
            "warning": "yellow",
            "info": "blue",
            "pending": "yellow",
            "completed": "green",
            "failed": "red",
        }

        color = status_colors.get(status.lower(), "white")
        status_text = Text(f"[{status.upper()}]", style=f"bold {color}")
        self._console.print(status_text, message)
