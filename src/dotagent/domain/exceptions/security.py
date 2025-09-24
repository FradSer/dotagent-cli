"""Security-related exceptions."""

from typing import Optional

from .base import DomainError


class SecurityError(DomainError):
    """Base class for security-related errors."""

    pass


class PathTraversalError(SecurityError):
    """Raised when a path traversal attack is detected."""

    def __init__(self, attempted_path: str) -> None:
        message = f"Path traversal detected: {attempted_path}"
        suggestion = "Use relative paths within the project directory only"

        super().__init__(
            message=message,
            details={"attempted_path": attempted_path},
            suggestion=suggestion,
        )


class InvalidPathError(SecurityError):
    """Raised when a file path is invalid or unsafe."""

    def __init__(self, path: str, reason: Optional[str] = None) -> None:
        message = f"Invalid or unsafe path: {path}"
        if reason:
            message += f" ({reason})"

        suggestion = (
            "Ensure the path is within allowed directories and properly formatted"
        )

        super().__init__(
            message=message,
            details={"path": path, "reason": reason},
            suggestion=suggestion,
        )


class PermissionDeniedError(SecurityError):
    """Raised when access to a resource is denied."""

    def __init__(self, resource: str, operation: str) -> None:
        message = f"Permission denied: cannot {operation} {resource}"
        suggestion = "Check file permissions or run with appropriate privileges"

        super().__init__(
            message=message,
            details={"resource": resource, "operation": operation},
            suggestion=suggestion,
        )


class UnsafeOperationError(SecurityError):
    """Raised when attempting a potentially unsafe operation."""

    def __init__(self, operation: str, details: Optional[str] = None) -> None:
        message = f"Unsafe operation blocked: {operation}"
        if details:
            message += f" ({details})"

        suggestion = "Use --force flag if you're sure this operation is safe"

        super().__init__(
            message=message,
            details={"operation": operation, "details": details},
            suggestion=suggestion,
        )
