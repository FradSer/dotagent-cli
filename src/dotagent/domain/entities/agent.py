"""Agent entity representing AI agents for Claude Code."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from ..exceptions import SyncValidationError


class AgentType(Enum):
    """Types of AI agents."""

    GLOBAL = "global"
    LOCAL = "local"


@dataclass(frozen=True)
class Agent:
    """Represents an AI agent configuration.

    This entity encapsulates agent-specific business logic
    and validation rules.
    """

    name: str
    agent_type: AgentType
    path: Path
    description: Optional[str] = None
    specializations: Optional[list[str]] = None

    def __post_init__(self) -> None:
        """Validate agent configuration."""
        validation_errors = []

        if not self.name:
            validation_errors.append("Agent name cannot be empty")

        if not self._is_valid_agent_name(self.name):
            validation_errors.append(f"Invalid agent name: {self.name}")

        if not self.path:
            validation_errors.append("Agent path cannot be empty")

        if validation_errors:
            raise SyncValidationError(validation_errors)

        # Set default empty list for specializations if None
        object.__setattr__(self, "specializations", self.specializations or [])

    def _is_valid_agent_name(self, name: str) -> bool:
        """Validate agent name according to naming conventions."""
        if not name:
            return False

        # Agent names should be lowercase with hyphens
        if not name.islower():
            return False

        # Should only contain letters, numbers, and hyphens
        allowed_chars = set("abcdefghijklmnopqrstuvwxyz0123456789-")
        if not set(name).issubset(allowed_chars):
            return False

        # Should not start or end with hyphen
        if name.startswith("-") or name.endswith("-"):
            return False

        # Should not have consecutive hyphens
        if "--" in name:
            return False

        return True

    @property
    def exists(self) -> bool:
        """Check if the agent file exists."""
        return self.path.exists() and self.path.is_file()

    @property
    def size(self) -> Optional[int]:
        """Get the size of the agent file in bytes."""
        if not self.exists:
            return None
        return self.path.stat().st_size

    @property
    def filename(self) -> str:
        """Get the agent filename."""
        return self.path.name

    @property
    def directory(self) -> Path:
        """Get the agent directory."""
        return self.path.parent

    @property
    def is_yaml(self) -> bool:
        """Check if the agent is a YAML file."""
        return self.path.suffix.lower() in [".yaml", ".yml"]

    @property
    def is_markdown(self) -> bool:
        """Check if the agent is a Markdown file."""
        return self.path.suffix.lower() in [".md", ".markdown"]

    @property
    def type(self) -> str:
        """Get the agent type as string for compatibility."""
        return self.agent_type.value

    def read_content(self) -> Optional[str]:
        """Read the agent file content."""
        if not self.exists:
            return None

        try:
            with open(self.path, encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None

    def get_tags(self) -> list[str]:
        """Extract tags from agent content or metadata."""
        tags = []

        # Add type as a tag
        tags.append(self.agent_type.value)

        # Add specializations as tags
        if self.specializations:
            tags.extend(self.specializations)

        # Add file type as tag
        if self.is_yaml:
            tags.append("yaml")
        elif self.is_markdown:
            tags.append("markdown")

        return list(set(tags))  # Remove duplicates

    def matches_search(self, query: str) -> bool:
        """Check if the agent matches a search query."""
        query_lower = query.lower()

        # Check name
        if query_lower in self.name.lower():
            return True

        # Check description
        if self.description and query_lower in self.description.lower():
            return True

        # Check specializations
        if self.specializations:
            for spec in self.specializations:
                if query_lower in spec.lower():
                    return True

        # Check tags
        for tag in self.get_tags():
            if query_lower in tag.lower():
                return True

        return False

    def copy_to(self, target_path: Path, overwrite: bool = False) -> bool:
        """Copy this agent to a target location."""
        if not self.exists:
            return False

        if target_path.exists() and not overwrite:
            return False

        try:
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file
            import shutil

            shutil.copy2(self.path, target_path)
            return True
        except Exception:
            return False

    def to_dict(self) -> dict[str, Any]:
        """Convert the agent to a dictionary representation."""
        return {
            "name": self.name,
            "type": self.agent_type.value,
            "path": str(self.path),
            "description": self.description,
            "specializations": self.specializations,
            "exists": self.exists,
            "size": self.size,
            "filename": self.filename,
            "tags": self.get_tags(),
        }

    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.name} ({self.agent_type.value})"
