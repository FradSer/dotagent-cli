"""Path validation specialist."""

from pathlib import Path

from ...domain.exceptions import SyncValidationError
from ..services.security_service import SecurityServiceImpl


class PathValidator:
    """Specialized validator for file paths."""

    def __init__(self) -> None:
        """Initialize path validator with security service."""
        self._security_service = SecurityServiceImpl()

    def validate(self, path: str) -> Path:
        """Validate and sanitize a file path."""
        if not path or not path.strip():
            raise SyncValidationError(["Path cannot be empty"])

        try:
            return self._security_service.sanitize_path(path)
        except Exception as e:
            raise SyncValidationError([f"Invalid path: {e}"])
