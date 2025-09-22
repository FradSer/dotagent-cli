"""Error boundary for handling and recovering from exceptions."""

import logging
import traceback
from functools import wraps
from typing import Any, Callable, Optional, Union

from ...domain.exceptions import DomainError, DotClaudeError, InfrastructureError
from ...interfaces.services import ConsoleService
from .error_formatter import ErrorFormatter
from .error_recovery import ErrorRecovery


class ErrorBoundary:
    """Error boundary that catches, logs, and handles exceptions gracefully."""

    def __init__(
        self,
        console_service: ConsoleService,
        logger: Optional[logging.Logger] = None,
        enable_recovery: bool = True,
        debug_mode: bool = False,
    ) -> None:
        """Initialize error boundary.

        Args:
            console_service: Service for console output
            logger: Logger for error logging
            enable_recovery: Whether to attempt error recovery
            debug_mode: Whether to show debug information
        """
        self._console = console_service
        self._logger = logger or logging.getLogger(__name__)
        self._formatter = ErrorFormatter(console_service)
        self._recovery = ErrorRecovery(console_service) if enable_recovery else None
        self._debug_mode = debug_mode

    def handle_exception(
        self,
        exception: Exception,
        context: Optional[str] = None,
        suggest_recovery: bool = True,
    ) -> bool:
        """Handle an exception with appropriate user messaging and recovery.

        Args:
            exception: The exception to handle
            context: Additional context about what was happening
            suggest_recovery: Whether to suggest recovery actions

        Returns:
            True if the error was handled gracefully, False if it should propagate
        """
        try:
            # Log the exception with full traceback
            self._log_exception(exception, context)

            # Format and display user-friendly error message
            self._formatter.format_and_display_error(exception, context)

            # Attempt recovery if enabled and appropriate
            if (
                suggest_recovery
                and self._recovery
                and self._should_attempt_recovery(exception)
            ):
                recovery_success = self._recovery.attempt_recovery(exception)
                if recovery_success:
                    self._console.print_success("Issue resolved automatically")
                    return True

            # Show debug information if enabled
            if self._debug_mode:
                self._show_debug_info(exception)

            return True  # Error was handled gracefully

        except Exception as e:
            # Meta-error: error in error handling
            self._logger.error(f"Error in error handling: {e}")
            self._console.print_error(
                f"An unexpected error occurred while handling the original error: {e}"
            )
            return False

    def _log_exception(self, exception: Exception, context: Optional[str]) -> None:
        """Log the exception with appropriate level and detail."""
        error_context = f" (Context: {context})" if context else ""

        if isinstance(exception, DomainError):
            # Domain errors are usually validation or business rule violations
            self._logger.warning(f"Domain error: {exception}{error_context}")
        elif isinstance(exception, InfrastructureError):
            # Infrastructure errors are external system failures
            self._logger.error(f"Infrastructure error: {exception}{error_context}")
        elif isinstance(exception, DotClaudeError):
            # Other application errors
            self._logger.error(f"Application error: {exception}{error_context}")
        else:
            # Unexpected errors
            self._logger.error(
                f"Unexpected error: {exception}{error_context}", exc_info=True
            )

    def _should_attempt_recovery(self, exception: Exception) -> bool:
        """Determine if recovery should be attempted for this exception."""
        # Don't attempt recovery for certain types of errors
        non_recoverable_types = [
            KeyboardInterrupt,
            SystemExit,
            MemoryError,
        ]

        return not any(
            isinstance(exception, error_type) for error_type in non_recoverable_types
        )

    def _show_debug_info(self, exception: Exception) -> None:
        """Show debug information about the exception."""
        debug_info = [
            f"Exception Type: {type(exception).__name__}",
            f"Exception Module: {type(exception).__module__}",
            f"Exception Args: {exception.args}",
        ]

        if hasattr(exception, "__traceback__") and exception.__traceback__:
            debug_info.append("Traceback:")
            debug_info.extend(traceback.format_tb(exception.__traceback__))

        self._console.print_panel(
            "\n".join(debug_info), title="Debug Information", style="yellow"
        )

    def catch(
        self,
        exceptions: Union[type[Exception], tuple[type[Exception], ...]] = Exception,
        context: Optional[str] = None,
        suggest_recovery: bool = True,
        reraise: bool = False,
    ) -> Callable:
        """Decorator to catch and handle exceptions in functions.

        Args:
            exceptions: Exception type(s) to catch
            context: Context description for error reporting
            suggest_recovery: Whether to suggest recovery actions
            reraise: Whether to reraise the exception after handling

        Returns:
            Decorator function
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    function_context = context or f"executing {func.__name__}"
                    handled = self.handle_exception(
                        e, function_context, suggest_recovery
                    )

                    if reraise or not handled:
                        raise

                    # Return None for gracefully handled errors
                    return None

            return wrapper

        return decorator

    def safe_execute(
        self,
        func: Callable,
        *args: Any,
        context: Optional[str] = None,
        default_return: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Safely execute a function with error boundary protection.

        Args:
            func: Function to execute
            *args: Positional arguments for the function
            context: Context description for error reporting
            default_return: Value to return if an error occurs
            **kwargs: Keyword arguments for the function

        Returns:
            Function result or default_return if an error occurred
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            function_context = context or f"executing {func.__name__}"
            self.handle_exception(e, function_context)
            return default_return


# Global error boundary instance (can be configured)
_global_error_boundary: Optional[ErrorBoundary] = None


def get_global_error_boundary() -> Optional[ErrorBoundary]:
    """Get the global error boundary instance."""
    return _global_error_boundary


def set_global_error_boundary(error_boundary: ErrorBoundary) -> None:
    """Set the global error boundary instance."""
    global _global_error_boundary
    _global_error_boundary = error_boundary


def with_error_boundary(
    exceptions: Union[type[Exception], tuple[type[Exception], ...]] = Exception,
    context: Optional[str] = None,
    suggest_recovery: bool = True,
) -> Callable:
    """Decorator that uses the global error boundary to handle exceptions.

    Args:
        exceptions: Exception type(s) to catch
        context: Context description for error reporting
        suggest_recovery: Whether to suggest recovery actions

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            boundary = get_global_error_boundary()
            if boundary:
                return boundary.safe_execute(func, *args, context=context, **kwargs)
            else:
                # Fallback: just execute the function
                return func(*args, **kwargs)

        return wrapper

    return decorator
