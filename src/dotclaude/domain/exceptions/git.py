"""Git-related exceptions."""

from typing import Optional

from .base import InfrastructureError


class GitOperationError(InfrastructureError):
    """Base class for Git operation failures."""

    pass


class RepositoryNotFoundError(GitOperationError):
    """Raised when a Git repository is not found or inaccessible."""

    def __init__(self, repo_url: str, details: Optional[str] = None) -> None:
        message = f"Repository not found or inaccessible: {repo_url}"
        if details:
            message += f" ({details})"

        suggestion = (
            "Check that the repository URL is correct and you have access permissions. "
            "For private repositories, ensure your SSH keys or authentication tokens are configured."
        )

        super().__init__(
            message=message,
            details={"repo_url": repo_url, "details": details},
            suggestion=suggestion,
        )


class BranchNotFoundError(GitOperationError):
    """Raised when a specified Git branch does not exist."""

    def __init__(self, branch_name: str, repo_url: Optional[str] = None) -> None:
        message = f"Branch '{branch_name}' not found"
        if repo_url:
            message += f" in repository {repo_url}"

        suggestion = (
            f"Check that branch '{branch_name}' exists in the repository. "
            "Use 'git branch -r' to list available remote branches."
        )

        super().__init__(
            message=message,
            details={"branch_name": branch_name, "repo_url": repo_url},
            suggestion=suggestion,
        )


class GitAuthenticationError(GitOperationError):
    """Raised when Git authentication fails."""

    def __init__(self, repo_url: str) -> None:
        message = f"Authentication failed for repository: {repo_url}"
        suggestion = (
            "Check your Git credentials. For SSH, ensure your SSH key is added to the agent. "
            "For HTTPS, check your username/password or personal access token."
        )

        super().__init__(
            message=message, details={"repo_url": repo_url}, suggestion=suggestion
        )


class DirtyWorkingDirectoryError(GitOperationError):
    """Raised when Git operations require a clean working directory."""

    def __init__(self, repo_path: str) -> None:
        message = f"Working directory has uncommitted changes: {repo_path}"
        suggestion = "Commit or stash your changes before proceeding."

        super().__init__(
            message=message, details={"repo_path": repo_path}, suggestion=suggestion
        )
