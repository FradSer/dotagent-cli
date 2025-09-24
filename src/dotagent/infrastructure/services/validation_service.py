"""Validation service implementation."""

from pathlib import Path
from typing import Any

from ...interfaces.services import ValidationService
from ..validators.agent_validator import AgentNameValidator
from ..validators.branch_validator import BranchNameValidator
from ..validators.config_validator import ConfigValidator
from ..validators.path_validator import PathValidator
from ..validators.url_validator import URLValidator


class ValidationServiceImpl(ValidationService):
    """Implementation of validation service using specialized validators."""

    def __init__(self) -> None:
        """Initialize validation service with specialized validators."""
        self._url_validator = URLValidator()
        self._branch_validator = BranchNameValidator()
        self._path_validator = PathValidator()
        self._agent_validator = AgentNameValidator()
        self._config_validator = ConfigValidator()

    def validate_path(self, path: str) -> Path:
        """Validate and sanitize a file path."""
        return self._path_validator.validate(path)

    def validate_url(self, url: str) -> str:
        """Validate a repository URL."""
        return self._url_validator.validate(url)

    def validate_branch_name(self, branch: str) -> str:
        """Validate a Git branch name."""
        return self._branch_validator.validate(branch)

    def validate_agent_name(self, name: str) -> str:
        """Validate an agent name."""
        return self._agent_validator.validate(name)

    def validate_config_key(self, key: str) -> str:
        """Validate a configuration key."""
        return self._config_validator.validate_key(key)

    def validate_config_value(self, key: str, value: Any) -> Any:
        """Validate a configuration value."""
        return self._config_validator.validate_value(key, value)
