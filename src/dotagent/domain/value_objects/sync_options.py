"""Sync operation value objects."""

import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class ConflictResolution(Enum):
    """Strategy for resolving sync conflicts."""

    LOCAL = "local"
    REMOTE = "remote"
    PROMPT = "prompt"
    ABORT = "abort"


class SyncOptions(BaseModel):
    """Value object representing sync operation configuration.

    This immutable object encapsulates all options for a sync operation,
    ensuring consistency and validation of sync parameters.
    """

    # Operation type
    pull_only: bool = Field(default=False, description="Only pull from remote")
    push_only: bool = Field(default=False, description="Only push to remote")

    # Conflict resolution
    conflict_resolution: ConflictResolution = Field(
        default=ConflictResolution.REMOTE,
        description="Strategy for resolving conflicts",
    )
    force: bool = Field(default=False, description="Force operation without prompts")

    # Preview and safety
    dry_run: bool = Field(default=False, description="Preview changes without applying")
    interactive: bool = Field(default=True, description="Allow interactive prompts")

    # Repository settings
    branch: str = Field(
        default="main", min_length=1, max_length=250, description="Git branch name"
    )
    repository_url: Optional[str] = Field(default=None, description="Repository URL")

    # Filtering
    include_patterns: Optional[list[str]] = Field(
        default=None, description="Patterns to include"
    )
    exclude_patterns: Optional[list[str]] = Field(
        default=None, description="Patterns to exclude"
    )

    # Local agents handling
    include_local_agents: bool = Field(
        default=False, description="Include project-specific agents in sync"
    )

    model_config = {
        "frozen": True,  # Make immutable
        "use_enum_values": True,
        "validate_assignment": True,
    }

    @field_validator("branch")
    def validate_branch_name(cls, v: str) -> str:
        """Validate Git branch name according to Git rules."""
        if not v or not v.strip():
            raise ValueError("Branch name cannot be empty")

        # Git branch name rules (simplified)
        invalid_chars = [" ", "~", "^", ":", "?", "*", "[", "\\"]
        if any(char in v for char in invalid_chars):
            raise ValueError(f"Branch name contains invalid characters: {v}")

        if v.startswith(".") or v.endswith("."):
            raise ValueError("Branch name cannot start or end with a dot")

        if v.startswith("/") or v.endswith("/"):
            raise ValueError("Branch name cannot start or end with a slash")

        if "//" in v:
            raise ValueError("Branch name cannot contain consecutive slashes")

        return v.strip()

    @field_validator("repository_url")
    def validate_repository_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate repository URL format."""
        if v is None:
            return v

        v = v.strip()
        if not v:
            return None

        # URL validation patterns:
        # 1. Full HTTPS/HTTP URLs: https://github.com/user/repo
        # 2. SSH URLs: git@github.com:user/repo.git
        # 3. Short format: user/repo (expanded by ConfigManager)
        url_pattern = re.compile(
            r"^(https?|git|ssh)://[^\s/$.?#].[^\s]*$|"  # Full URLs
            r"^git@[^\s:]+:[^\s]+\.git$|"  # SSH URLs
            r"^[a-zA-Z0-9\-_.]+/[a-zA-Z0-9\-_.]+$"  # Short format: user/repo
        )

        if not url_pattern.match(v):
            raise ValueError(f"Invalid repository URL format: {v}")

        return v

    @model_validator(mode="after")
    def validate_operation_consistency(self) -> "SyncOptions":
        """Validate that operation options are consistent."""
        # Can't be both pull-only and push-only
        if self.pull_only and self.push_only:
            raise ValueError("Cannot specify both pull_only and push_only")

        # Interactive mode requires non-dry-run for prompts to work
        if (
            self.interactive
            and self.dry_run
            and self.conflict_resolution == ConflictResolution.PROMPT
        ):
            raise ValueError("Interactive prompting not available in dry-run mode")

        return self

    @property
    def is_bidirectional(self) -> bool:
        """Check if this is a bidirectional sync operation."""
        return not self.pull_only and not self.push_only

    @property
    def is_unidirectional(self) -> bool:
        """Check if this is a unidirectional sync operation."""
        return self.pull_only or self.push_only

    @property
    def operation_type(self) -> str:
        """Get a human-readable operation type."""
        if self.pull_only:
            return "pull"
        elif self.push_only:
            return "push"
        else:
            return "bidirectional sync"

    @property
    def requires_prompts(self) -> bool:
        """Check if this operation might require user prompts."""
        return (
            self.interactive
            and not self.force
            and not self.dry_run
            and self.conflict_resolution == ConflictResolution.PROMPT
        )

    def with_force(self) -> "SyncOptions":
        """Create a new SyncOptions with force enabled."""
        return SyncOptions(
            pull_only=self.pull_only,
            push_only=self.push_only,
            conflict_resolution=self.conflict_resolution,
            force=True,  # Override force
            dry_run=self.dry_run,
            interactive=self.interactive,
            branch=self.branch,
            repository_url=self.repository_url,
            include_patterns=self.include_patterns,
            exclude_patterns=self.exclude_patterns,
            include_local_agents=self.include_local_agents,
        )

    def with_dry_run(self, dry_run: bool = True) -> "SyncOptions":
        """Create a new SyncOptions with dry_run setting."""
        return SyncOptions(
            pull_only=self.pull_only,
            push_only=self.push_only,
            conflict_resolution=self.conflict_resolution,
            force=self.force,
            dry_run=dry_run,  # Override dry_run
            interactive=self.interactive,
            branch=self.branch,
            repository_url=self.repository_url,
            include_patterns=self.include_patterns,
            exclude_patterns=self.exclude_patterns,
            include_local_agents=self.include_local_agents,
        )

    def with_branch(self, branch: str) -> "SyncOptions":
        """Create a new SyncOptions with different branch."""
        return SyncOptions(
            pull_only=self.pull_only,
            push_only=self.push_only,
            conflict_resolution=self.conflict_resolution,
            force=self.force,
            dry_run=self.dry_run,
            interactive=self.interactive,
            branch=branch,  # Override branch
            repository_url=self.repository_url,
            include_patterns=self.include_patterns,
            exclude_patterns=self.exclude_patterns,
            include_local_agents=self.include_local_agents,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "pull_only": self.pull_only,
            "push_only": self.push_only,
            "conflict_resolution": self.conflict_resolution.value,
            "force": self.force,
            "dry_run": self.dry_run,
            "interactive": self.interactive,
            "branch": self.branch,
            "repository_url": self.repository_url,
            "include_patterns": self.include_patterns,
            "exclude_patterns": self.exclude_patterns,
            "include_local_agents": self.include_local_agents,
        }
