"""Configuration key value objects."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ConfigScope(Enum):
    """Configuration scope enumeration."""

    LOCAL = "local"
    GLOBAL = "global"
    SYSTEM = "system"


@dataclass(frozen=True)
class ConfigKey:
    """Value object representing a configuration key."""

    key: str
    scope: ConfigScope = ConfigScope.GLOBAL
    description: Optional[str] = None
    default_value: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate configuration key."""
        if not self.key or not self.key.strip():
            raise ValueError("Configuration key cannot be empty")

        if "." not in self.key:
            raise ValueError(
                "Configuration key must contain at least one dot separator"
            )

    @property
    def namespace(self) -> str:
        """Get the namespace part of the key."""
        return self.key.split(".")[0]

    @property
    def name(self) -> str:
        """Get the name part of the key."""
        parts = self.key.split(".")
        return ".".join(parts[1:]) if len(parts) > 1 else ""

    def __str__(self) -> str:
        """String representation of the config key."""
        return f"{self.key} ({self.scope.value})"
