"""Repository entity representing a Git repository."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from ..exceptions import SyncValidationError


@dataclass(frozen=True)
class Repository:
    """Represents a Git repository with its configuration.

    This entity encapsulates repository-specific business logic
    and validation rules.
    """

    url: str
    branch: str
    local_path: Optional[Path] = None

    def __post_init__(self) -> None:
        """Validate repository configuration."""
        validation_errors = []

        if not self.url:
            validation_errors.append("Repository URL cannot be empty")

        if not self.branch:
            validation_errors.append("Branch name cannot be empty")

        if not self._is_valid_url(self.url):
            validation_errors.append(f"Invalid repository URL: {self.url}")

        try:
            from ...infrastructure.validators.branch_validator import (
                BranchNameValidator,
            )

            BranchNameValidator().validate(self.branch)
        except Exception:
            validation_errors.append(f"Invalid branch name: {self.branch}")

        if validation_errors:
            raise SyncValidationError(validation_errors)

    def _is_valid_url(self, url: str) -> bool:
        """Validate if the URL is a valid Git repository URL."""
        try:
            parsed = urlparse(url)
            # Check for common Git URL patterns
            if parsed.scheme in ["http", "https", "ssh", "git"]:
                return True
            # SSH URLs like git@github.com:user/repo.git
            if "@" in url and ":" in url:
                return True
            return False
        except Exception:
            return False

    @property
    def is_github(self) -> bool:
        """Check if this is a GitHub repository."""
        return "github.com" in self.url.lower()

    @property
    def is_gitlab(self) -> bool:
        """Check if this is a GitLab repository."""
        return "gitlab.com" in self.url.lower()

    @property
    def is_ssh(self) -> bool:
        """Check if this repository uses SSH authentication."""
        return self.url.startswith("git@") or self.url.startswith("ssh://")

    @property
    def is_https(self) -> bool:
        """Check if this repository uses HTTPS."""
        return self.url.startswith("https://")

    @property
    def host(self) -> Optional[str]:
        """Extract the host from the repository URL."""
        try:
            if self.is_ssh and "@" in self.url:
                # Handle git@github.com:user/repo.git format
                return self.url.split("@")[1].split(":")[0]
            else:
                parsed = urlparse(self.url)
                return parsed.netloc
        except Exception:
            return None

    @property
    def owner_and_name(self) -> Optional[tuple[str, str]]:
        """Extract owner and repository name from URL."""
        try:
            if self.is_ssh and "@" in self.url:
                # Handle git@github.com:user/repo.git format
                path = self.url.split(":")[1]
            else:
                parsed = urlparse(self.url)
                path = parsed.path

            # Remove leading slash and .git suffix
            path = path.lstrip("/").rstrip(".git")
            parts = path.split("/")

            if len(parts) >= 2:
                return parts[0], parts[1]
        except Exception:
            pass
        return None

    @property
    def clone_url(self) -> str:
        """Get the URL for cloning the repository."""
        return self.url

    def get_web_url(self, file_path: Optional[str] = None) -> Optional[str]:
        """Get the web URL for viewing the repository or specific file."""
        if not self.is_github and not self.is_gitlab:
            return None

        owner_name = self.owner_and_name
        if not owner_name:
            return None

        owner, name = owner_name
        base_url = f"https://{self.host}/{owner}/{name}"

        if file_path:
            if self.is_github:
                return f"{base_url}/blob/{self.branch}/{file_path}"
            elif self.is_gitlab:
                return f"{base_url}/-/blob/{self.branch}/{file_path}"

        return base_url

    def __str__(self) -> str:
        """String representation of the repository."""
        return f"{self.url}#{self.branch}"
