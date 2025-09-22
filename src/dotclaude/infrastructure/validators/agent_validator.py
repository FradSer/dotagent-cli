"""Agent name validation specialist."""

import re

from ...domain.constants import ValidationLimits
from ...domain.exceptions import SyncValidationError


class AgentNameValidator:
    """Specialized validator for agent names."""

    _RESERVED_NAMES = ["system", "global", "local", "default", "config", "help"]

    def validate(self, name: str) -> str:
        """Validate an agent name."""
        if not name or not name.strip():
            raise SyncValidationError(["Agent name cannot be empty"])

        name = name.strip()
        validation_errors = []

        # Check length
        if len(name) < ValidationLimits.MIN_AGENT_NAME_LENGTH:
            validation_errors.append(
                f"Agent name must be at least {ValidationLimits.MIN_AGENT_NAME_LENGTH} characters long"
            )

        if len(name) > ValidationLimits.MAX_AGENT_NAME_LENGTH:
            validation_errors.append(
                f"Agent name too long (max {ValidationLimits.MAX_AGENT_NAME_LENGTH} characters)"
            )

        # Agent names should be lowercase with hyphens
        if not re.match(r"^[a-z0-9-]+$", name):
            validation_errors.append(
                "Agent name must contain only lowercase letters, numbers, and hyphens"
            )

        # Should not start or end with hyphen
        if name.startswith("-") or name.endswith("-"):
            validation_errors.append("Agent name cannot start or end with a hyphen")

        # Should not have consecutive hyphens
        if "--" in name:
            validation_errors.append("Agent name cannot contain consecutive hyphens")

        # Reserved names
        if name in self._RESERVED_NAMES:
            validation_errors.append(f"'{name}' is a reserved agent name")

        if validation_errors:
            raise SyncValidationError(validation_errors)

        return name
