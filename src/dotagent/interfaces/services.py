"""Service interfaces for cross-cutting concerns."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional


class ConsoleService(ABC):
    """Interface for console output operations."""

    @abstractmethod
    def print(self, message: str, style: Optional[str] = None) -> None:
        """Print a message to the console."""
        pass

    @abstractmethod
    def print_error(self, message: str) -> None:
        """Print an error message to the console."""
        pass

    @abstractmethod
    def print_warning(self, message: str) -> None:
        """Print a warning message to the console."""
        pass

    @abstractmethod
    def print_success(self, message: str) -> None:
        """Print a success message to the console."""
        pass

    @abstractmethod
    def print_table(
        self, data: list[dict[str, Any]], title: Optional[str] = None
    ) -> None:
        """Print data in a table format."""
        pass

    @abstractmethod
    def confirm(self, message: str, default: bool = False) -> bool:
        """Ask for user confirmation."""
        pass

    @abstractmethod
    def prompt(self, message: str, default: Optional[str] = None) -> str:
        """Prompt user for input."""
        pass

    @abstractmethod
    def select(self, message: str, choices: list[str]) -> str:
        """Let user select from a list of choices."""
        pass


class ValidationService(ABC):
    """Interface for validation operations."""

    @abstractmethod
    def validate_path(self, path: str) -> Path:
        """Validate and sanitize a file path."""
        pass

    @abstractmethod
    def validate_url(self, url: str) -> str:
        """Validate a repository URL."""
        pass

    @abstractmethod
    def validate_branch_name(self, branch: str) -> str:
        """Validate a Git branch name."""
        pass

    @abstractmethod
    def validate_agent_name(self, name: str) -> str:
        """Validate an agent name."""
        pass

    @abstractmethod
    def validate_config_key(self, key: str) -> str:
        """Validate a configuration key."""
        pass

    @abstractmethod
    def validate_config_value(self, key: str, value: Any) -> Any:
        """Validate a configuration value."""
        pass


class SecurityService(ABC):
    """Interface for security operations."""

    @abstractmethod
    def is_safe_path(self, path: Path, allowed_base: Optional[Path] = None) -> bool:
        """Check if a path is safe to access."""
        pass

    @abstractmethod
    def sanitize_path(self, path: str) -> Path:
        """Sanitize a path for safe access."""
        pass

    @abstractmethod
    def is_safe_url(self, url: str) -> bool:
        """Check if a URL is safe to access."""
        pass

    @abstractmethod
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename for safe use."""
        pass

    @abstractmethod
    def check_permissions(self, path: Path, operation: str) -> bool:
        """Check if we have permissions for an operation on a path."""
        pass

    @abstractmethod
    def mask_sensitive_data(self, data: str) -> str:
        """Mask sensitive data in strings (URLs, tokens, etc.)."""
        pass
