"""Configuration-related exceptions."""

from typing import Any, Optional

from .base import DomainError


class ConfigurationError(DomainError):
    """Base class for configuration-related errors."""

    pass


class ConfigNotFoundError(ConfigurationError):
    """Raised when a required configuration file or key is not found."""

    def __init__(
        self,
        config_key: Optional[str] = None,
        config_path: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        if config_key and config_path:
            message = f"Configuration key '{config_key}' not found in {config_path}"
        elif config_key:
            message = f"Configuration key '{config_key}' not found"
        elif config_path:
            message = f"Configuration file not found: {config_path}"
        else:
            message = "Configuration not found"

        if not suggestion:
            if config_key:
                suggestion = f"Set the configuration with: dotclaude config set {config_key} <value>"
            else:
                suggestion = (
                    "Initialize configuration with: dotclaude config set <key> <value>"
                )

        super().__init__(
            message=message,
            details={"config_key": config_key, "config_path": config_path},
            suggestion=suggestion,
        )


class InvalidConfigError(ConfigurationError):
    """Raised when configuration values are invalid."""

    def __init__(
        self,
        config_key: str,
        value: Any,
        expected_type: Optional[str] = None,
        valid_values: Optional[list] = None,
    ) -> None:
        if valid_values:
            message = f"Invalid value '{value}' for config '{config_key}'. Valid values: {valid_values}"
            suggestion = f"Set a valid value: dotclaude config set {config_key} {valid_values[0]}"
        elif expected_type:
            message = f"Invalid value '{value}' for config '{config_key}'. Expected: {expected_type}"
            suggestion = f"Provide a {expected_type} value for {config_key}"
        else:
            message = f"Invalid configuration value for '{config_key}': {value}"
            suggestion = "Check the configuration documentation for valid values"

        super().__init__(
            message=message,
            details={
                "config_key": config_key,
                "value": value,
                "expected_type": expected_type,
                "valid_values": valid_values,
            },
            suggestion=suggestion,
        )
