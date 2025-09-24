"""Base exception classes for dotclaude application."""

from typing import Any, Optional


class DotClaudeError(Exception):
    """Base exception for all dotclaude operations.

    This is the root exception that all other domain exceptions inherit from.
    It provides a consistent interface for error handling throughout the application.
    """

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Additional context about the error
            suggestion: Suggested action for the user
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.suggestion = suggestion

    def __str__(self) -> str:
        """Return a formatted error message."""
        result = self.message
        if self.suggestion:
            result += f"\nSuggestion: {self.suggestion}"
        return result

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for structured logging."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "suggestion": self.suggestion,
        }


class DomainError(DotClaudeError):
    """Base class for domain-specific errors.

    These represent business rule violations or domain constraint failures.
    """

    pass


class InfrastructureError(DotClaudeError):
    """Base class for infrastructure-related errors.

    These represent failures in external systems like file system, Git, network, etc.
    """

    pass
