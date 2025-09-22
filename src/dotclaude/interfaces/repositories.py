"""Repository interfaces for data access."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

from ..domain.entities import Agent, Repository, SyncItem


class SyncRepository(ABC):
    """Interface for sync data operations."""

    @abstractmethod
    def get_sync_items(self) -> list[SyncItem]:
        """Get all items that can be synchronized."""
        pass

    @abstractmethod
    def get_sync_item(self, name: str) -> Optional[SyncItem]:
        """Get a specific sync item by name."""
        pass

    @abstractmethod
    def copy_item(self, item: SyncItem, source_to_dest: bool) -> bool:
        """Copy an item from source to destination."""
        pass

    @abstractmethod
    def delete_item(self, item: SyncItem, from_local: bool) -> bool:
        """Delete an item from local or remote location."""
        pass


class AgentRepository(ABC):
    """Interface for agent data operations."""

    @abstractmethod
    def get_all_agents(self) -> list[Agent]:
        """Get all available agents."""
        pass

    @abstractmethod
    def get_local_agents(self) -> list[Agent]:
        """Get all local agents."""
        pass

    @abstractmethod
    def get_global_agents(self) -> list[Agent]:
        """Get all global agents."""
        pass

    @abstractmethod
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get a specific agent by name."""
        pass

    @abstractmethod
    def copy_agent(
        self, agent: Agent, target_path: Path, overwrite: bool = False
    ) -> bool:
        """Copy an agent to a target location."""
        pass

    @abstractmethod
    def save_agent(self, agent: Agent) -> bool:
        """Save an agent configuration."""
        pass

    @abstractmethod
    def delete_agent(self, agent: Agent) -> bool:
        """Delete an agent."""
        pass


class ConfigRepository(ABC):
    """Interface for configuration data operations."""

    @abstractmethod
    def get_config(self, key: str, scope: Optional[str] = None) -> Optional[Any]:
        """Get a configuration value."""
        pass

    @abstractmethod
    def set_config(self, key: str, value: Any, scope: str = "global") -> None:
        """Set a configuration value."""
        pass

    @abstractmethod
    def unset_config(self, key: str, scope: str = "global") -> None:
        """Remove a configuration value."""
        pass

    @abstractmethod
    def get_all_config(self, scope: Optional[str] = None) -> dict[str, Any]:
        """Get all configuration values for a scope."""
        pass

    @abstractmethod
    def get_config_path(self, scope: str) -> Path:
        """Get the path to a configuration file."""
        pass


class GitRepository(ABC):
    """Interface for Git operations."""

    @abstractmethod
    def clone(self, repository: Repository, target_path: Path) -> bool:
        """Clone a repository to target path."""
        pass

    @abstractmethod
    def fetch(self, repo_path: Path, branch: str) -> bool:
        """Fetch updates from remote repository."""
        pass

    @abstractmethod
    def pull(self, repo_path: Path, branch: str) -> bool:
        """Pull changes from remote repository."""
        pass

    @abstractmethod
    def push(self, repo_path: Path, branch: str) -> bool:
        """Push changes to remote repository."""
        pass

    @abstractmethod
    def get_current_branch(self, repo_path: Path) -> Optional[str]:
        """Get the current branch of a repository."""
        pass

    @abstractmethod
    def switch_branch(self, repo_path: Path, branch: str) -> bool:
        """Switch to a different branch."""
        pass

    @abstractmethod
    def is_clean(self, repo_path: Path) -> bool:
        """Check if the working directory is clean."""
        pass

    @abstractmethod
    def get_status(self, repo_path: Path) -> dict[str, Any]:
        """Get the status of the repository."""
        pass


class FileSystemRepository(ABC):
    """Interface for file system operations."""

    @abstractmethod
    def copy_file(self, source: Path, destination: Path) -> bool:
        """Copy a file from source to destination."""
        pass

    @abstractmethod
    def copy_directory(self, source: Path, destination: Path) -> bool:
        """Copy a directory from source to destination."""
        pass

    @abstractmethod
    def delete_file(self, path: Path) -> bool:
        """Delete a file."""
        pass

    @abstractmethod
    def delete_directory(self, path: Path) -> bool:
        """Delete a directory and its contents."""
        pass

    @abstractmethod
    def create_directory(self, path: Path) -> bool:
        """Create a directory."""
        pass

    @abstractmethod
    def exists(self, path: Path) -> bool:
        """Check if a path exists."""
        pass

    @abstractmethod
    def is_file(self, path: Path) -> bool:
        """Check if a path is a file."""
        pass

    @abstractmethod
    def is_directory(self, path: Path) -> bool:
        """Check if a path is a directory."""
        pass

    @abstractmethod
    def get_size(self, path: Path) -> Optional[int]:
        """Get the size of a file or directory."""
        pass

    @abstractmethod
    def compare_files(self, path1: Path, path2: Path) -> bool:
        """Compare two files for equality."""
        pass

    @abstractmethod
    def compare_directories(self, path1: Path, path2: Path) -> dict[str, Any]:
        """Compare two directories and return differences."""
        pass
