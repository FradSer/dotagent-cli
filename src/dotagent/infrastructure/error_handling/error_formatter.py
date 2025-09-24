"""Error formatter for user-friendly error messages."""

import re
from typing import Optional

from ...domain.exceptions import (
    ConfigurationError,
    DotClaudeError,
    GitOperationError,
    SecurityError,
    SyncError,
)
from ...interfaces.services import ConsoleService


class ErrorFormatter:
    """Formats exceptions into user-friendly error messages."""

    def __init__(self, console_service: ConsoleService) -> None:
        """Initialize error formatter.

        Args:
            console_service: Service for console output
        """
        self._console = console_service

    def format_and_display_error(
        self,
        exception: Exception,
        context: Optional[str] = None,
    ) -> None:
        """Format and display an error message for the user.

        Args:
            exception: The exception to format
            context: Additional context about what was happening
        """
        if isinstance(exception, DotClaudeError):
            self._display_application_error(exception, context)
        else:
            self._display_system_error(exception, context)

    def _display_application_error(
        self,
        error: DotClaudeError,
        context: Optional[str] = None,
    ) -> None:
        """Display a user-friendly application error."""
        # Build error message parts
        title = self._get_error_title(error)
        message = self._format_error_message(error.message)
        suggestion = error.suggestion

        # Add context if provided
        if context:
            message = f"{message} (while {context})"

        # Display the error
        self._console.print_error(f"{title}: {message}")

        # Show suggestion if available
        if suggestion:
            self._console.print(f"Suggestion: {suggestion}", style="cyan")

        # Show details if available
        if error.details:
            self._display_error_details(error.details)

    def _display_system_error(
        self,
        error: Exception,
        context: Optional[str] = None,
    ) -> None:
        """Display a system error with helpful context."""
        error_type = type(error).__name__
        message = str(error) if str(error) else "An unexpected error occurred"

        # Clean up common system error messages
        message = self._clean_system_error_message(message)

        if context:
            message = f"{message} (while {context})"

        self._console.print_error(f"{error_type}: {message}")

        # Provide generic suggestions for common system errors
        suggestion = self._get_system_error_suggestion(error)
        if suggestion:
            self._console.print(f"Suggestion: {suggestion}", style="cyan")

    def _get_error_title(self, error: DotClaudeError) -> str:
        """Get a user-friendly title for the error type."""
        error_titles = {
            ConfigurationError: "Configuration Issue",
            GitOperationError: "Git Operation Failed",
            SyncError: "Sync Operation Failed",
            SecurityError: "Security Violation",
        }

        for error_type, title in error_titles.items():
            if isinstance(error, error_type):
                return title

        return "Application Error"

    def _format_error_message(self, message: str) -> str:
        """Format error message for better readability."""
        if not message:
            return "An error occurred"

        # Capitalize first letter
        message = (
            message[0].upper() + message[1:] if len(message) > 1 else message.upper()
        )

        # Remove trailing periods for consistency
        message = message.rstrip(".")

        return message

    def _clean_system_error_message(self, message: str) -> str:
        """Clean up system error messages to be more user-friendly."""
        # Remove file paths from common error messages
        patterns = [
            (r"No such file or directory: '([^']+)'", r"File not found: \1"),
            (r"Permission denied: '([^']+)'", r"Permission denied for: \1"),
            (r"\[Errno \d+\] ([^:]+): '([^']+)'", r"\1: \2"),
            (
                r"Command '([^']+)' returned non-zero exit status \d+",
                r"Command failed: \1",
            ),
        ]

        cleaned_message = message
        for pattern, replacement in patterns:
            cleaned_message = re.sub(pattern, replacement, cleaned_message)

        return cleaned_message

    def _get_system_error_suggestion(self, error: Exception) -> Optional[str]:
        """Get suggestions for common system errors."""
        error_message = str(error).lower()

        if "permission denied" in error_message:
            return "Check file permissions or try running with appropriate privileges"

        if "no such file or directory" in error_message:
            return "Verify the file path exists and is accessible"

        if "connection" in error_message or "network" in error_message:
            return "Check your internet connection and try again"

        if "timeout" in error_message:
            return "The operation timed out. Try again or check your connection"

        if isinstance(error, KeyboardInterrupt):
            return "Operation was cancelled by user (Ctrl+C)"

        if isinstance(error, FileNotFoundError):
            return "Make sure the required files exist and paths are correct"

        if isinstance(error, PermissionError):
            return "Check file permissions or run with appropriate privileges"

        return None

    def _display_error_details(self, details: dict) -> None:
        """Display error details in a structured format."""
        if not details:
            return

        self._console.print("\nError Details:", style="bold")
        for key, value in details.items():
            if value is not None:
                formatted_key = key.replace("_", " ").title()
                self._console.print(f"  {formatted_key}: {value}")

    def format_validation_errors(self, errors: list[str]) -> str:
        """Format a list of validation errors into a readable message."""
        if not errors:
            return "Validation failed"

        if len(errors) == 1:
            return f"Validation error: {errors[0]}"

        formatted_errors = []
        for i, error in enumerate(errors, 1):
            formatted_errors.append(f"  {i}. {error}")

        return f"Validation failed with {len(errors)} errors:\n" + "\n".join(
            formatted_errors
        )

    def format_progress_error(
        self,
        operation: str,
        current: int,
        total: int,
        error: Exception,
    ) -> str:
        """Format an error that occurred during a progress operation."""
        progress = f"{current}/{total}" if total > 0 else str(current)
        return f"Failed during {operation} at step {progress}: {error}"
