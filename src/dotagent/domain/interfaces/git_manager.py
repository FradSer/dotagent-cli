"""Git manager interface for dependency inversion."""

from abc import ABC, abstractmethod
from pathlib import Path


class GitManagerInterface(ABC):
    """Interface defining Git operations for dependency inversion."""

    @abstractmethod
    def clone_repo(self, url: str, branch: str, target_dir: Path) -> None:
        """Clone repository to target directory."""
        ...

    @abstractmethod
    def fetch_repo(self, branch: str) -> None:
        """Fetch latest changes from remote."""
        ...

    @abstractmethod
    def stage_all_changes(self) -> None:
        """Stage all changes in the repository."""
        ...

    @abstractmethod
    def create_commit(self, message: str) -> None:
        """Create a commit with the given message."""
        ...

    @abstractmethod
    def push_changes(self, branch: str) -> None:
        """Push changes to remote repository."""
        ...

    @abstractmethod
    def get_current_branch(self) -> str:
        """Get the current branch name."""
        ...

    @abstractmethod
    def branch_exists(self, branch: str, remote: bool = False) -> bool:
        """Check if a branch exists locally or remotely."""
        ...

    @abstractmethod
    def get_repo_status(self) -> dict:
        """Get repository status information."""
        ...

    @abstractmethod
    def check_connectivity(self, url: str) -> bool:
        """Check if we can connect to the remote repository."""
        ...
