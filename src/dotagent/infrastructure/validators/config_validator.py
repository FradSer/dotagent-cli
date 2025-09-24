"""Configuration validation specialist."""

import re
from typing import Any

from ...domain.constants import ValidationLimits
from ...domain.exceptions import InvalidConfigError


class ConfigValidator:
    """Specialized validator for configuration keys and values."""

    _VALID_NAMESPACES = ["sync", "agent", "config", "git", "ui", "security"]

    def validate_key(self, key: str) -> str:
        """Validate a configuration key."""
        if not key or not key.strip():
            raise InvalidConfigError("config_key", key, "string", ["non-empty string"])

        key = key.strip()
        validation_errors = []

        # Config keys should have namespace.key format
        if "." not in key:
            validation_errors.append(
                "Configuration key must contain at least one dot separator (namespace.key)"
            )

        # Check for valid characters
        if not re.match(r"^[a-z0-9._-]+$", key, re.IGNORECASE):
            validation_errors.append(
                "Configuration key can only contain letters, numbers, dots, underscores, and hyphens"
            )

        # Check length
        if len(key) > 200:
            validation_errors.append("Configuration key too long (max 200 characters)")

        # Check parts
        parts = key.split(".")
        for part in parts:
            if not part:
                validation_errors.append("Configuration key cannot have empty parts")
            elif part.startswith("-") or part.endswith("-"):
                validation_errors.append(
                    "Configuration key parts cannot start or end with hyphens"
                )

        # Validate namespace (first part)
        if parts:
            namespace = parts[0]
            if namespace not in self._VALID_NAMESPACES:
                validation_errors.append(
                    f"Unknown configuration namespace: {namespace}. Valid: {self._VALID_NAMESPACES}"
                )

        if validation_errors:
            raise InvalidConfigError(
                "config_key", key, expected_type="valid config key", valid_values=None
            )

        return key

    def validate_value(self, key: str, value: Any) -> Any:
        """Validate a configuration value based on the key pattern."""
        if value is None:
            return value

        # Type validation based on key patterns
        if key.endswith(".url"):
            if not isinstance(value, str):
                raise InvalidConfigError(key, value, "string (URL)")
            from .url_validator import URLValidator

            return URLValidator().validate(value)

        elif key.endswith(".branch"):
            if not isinstance(value, str):
                raise InvalidConfigError(key, value, "string (branch name)")
            from .branch_validator import BranchNameValidator

            return BranchNameValidator().validate(value)

        elif key.endswith(".path"):
            if not isinstance(value, str):
                raise InvalidConfigError(key, value, "string (file path)")
            from .path_validator import PathValidator

            validated_path = PathValidator().validate(value)
            return str(validated_path)

        elif key.endswith((".enabled", ".force", ".dry_run")):
            if isinstance(value, str):
                # Convert string boolean values
                if value.lower() in ["true", "yes", "1", "on"]:
                    return True
                elif value.lower() in ["false", "no", "0", "off"]:
                    return False
                else:
                    raise InvalidConfigError(key, value, "boolean", ["true", "false"])
            elif not isinstance(value, bool):
                raise InvalidConfigError(key, value, "boolean")
            return value

        elif "prefer" in key:
            if not isinstance(value, str):
                raise InvalidConfigError(key, value, "string")
            valid_values = ["local", "remote"]
            if value not in valid_values:
                raise InvalidConfigError(key, value, valid_values=valid_values)
            return value

        # Default: convert to string and validate length
        str_value = str(value)
        if len(str_value) > ValidationLimits.MAX_CONFIG_VALUE_LENGTH:
            raise InvalidConfigError(
                key,
                value,
                f"string (max {ValidationLimits.MAX_CONFIG_VALUE_LENGTH} characters)",
            )

        return str_value
