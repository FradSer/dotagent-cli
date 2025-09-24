"""Git operations manager using GitPython."""

import subprocess
from pathlib import Path
from typing import Optional

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

from dotagent.utils.console import console


class GitManager:
    """Manages Git operations for repository synchronization."""

    def __init__(self):
        self.repo: Optional[Repo] = None

    def clone_repo(self, url: str, branch: str, target_dir: Path) -> None:
        """Clone repository to target directory."""
        try:
            console.print(f"[info]Cloning {url} (branch: {branch})[/info]")
            self.repo = Repo.clone_from(url, target_dir, branch=branch)
            console.print("[success]Repository cloned successfully[/success]")
        except GitCommandError as e:
            raise Exception(f"Failed to clone repository: {e}")

    def fetch_repo(self, branch: str) -> None:
        """Fetch latest changes from remote."""
        try:
            if not self.repo:
                self.repo = Repo(Path.cwd())

            origin = self.repo.remotes.origin
            origin.fetch()

            # Switch to target branch if needed
            current_branch = self.repo.active_branch.name
            if current_branch != branch:
                if branch in [ref.name for ref in self.repo.heads]:
                    self.repo.heads[branch].checkout()
                else:
                    # Create and checkout new branch from remote
                    self.repo.create_head(branch, f"origin/{branch}")
                    self.repo.heads[branch].checkout()

            # Pull latest changes
            origin.pull()
            console.print(
                f"[success]Fetched latest changes for branch: {branch}[/success]"
            )

        except (GitCommandError, InvalidGitRepositoryError) as e:
            raise Exception(f"Failed to fetch repository: {e}")

    def stage_all_changes(self) -> None:
        """Stage all changes in the repository."""
        try:
            if not self.repo:
                self.repo = Repo(Path.cwd())

            self.repo.git.add(A=True)
            console.print("[info]Staged all changes[/info]")

        except GitCommandError as e:
            raise Exception(f"Failed to stage changes: {e}")

    def create_commit(self, message: str) -> None:
        """Create a commit with the given message."""
        try:
            if not self.repo:
                self.repo = Repo(Path.cwd())

            # Check if there are any changes to commit
            if not self.repo.is_dirty() and not self.repo.untracked_files:
                console.print("[info]No changes to commit[/info]")
                return

            self.repo.index.commit(message)
            console.print(f"[success]Created commit: {message}[/success]")

        except GitCommandError as e:
            raise Exception(f"Failed to create commit: {e}")

    def push_changes(self, branch: str) -> None:
        """Push changes to remote repository."""
        try:
            if not self.repo:
                self.repo = Repo(Path.cwd())

            origin = self.repo.remotes.origin
            origin.push(branch)
            console.print(f"[success]Pushed changes to {branch}[/success]")

        except GitCommandError as e:
            raise Exception(f"Failed to push changes: {e}")

    def get_current_branch(self) -> str:
        """Get the current branch name."""
        try:
            if not self.repo:
                self.repo = Repo(Path.cwd())

            return self.repo.active_branch.name

        except (GitCommandError, InvalidGitRepositoryError):
            return "main"  # Default fallback

    def branch_exists(self, branch: str, remote: bool = False) -> bool:
        """Check if a branch exists locally or remotely."""
        try:
            if not self.repo:
                self.repo = Repo(Path.cwd())

            if remote:
                return f"origin/{branch}" in [
                    ref.name for ref in self.repo.remotes.origin.refs
                ]
            else:
                return branch in [ref.name for ref in self.repo.heads]

        except (GitCommandError, InvalidGitRepositoryError):
            return False

    def get_repo_status(self) -> dict:
        """Get repository status information."""
        try:
            if not self.repo:
                self.repo = Repo(Path.cwd())

            return {
                "dirty": self.repo.is_dirty(),
                "untracked_files": len(self.repo.untracked_files),
                "current_branch": self.get_current_branch(),
                "has_remote": len(list(self.repo.remotes)) > 0,
            }

        except (GitCommandError, InvalidGitRepositoryError):
            return {
                "dirty": False,
                "untracked_files": 0,
                "current_branch": "unknown",
                "has_remote": False,
            }

    def check_connectivity(self, url: str) -> bool:
        """Check if we can connect to the remote repository."""
        try:
            # Use git ls-remote to check connectivity
            result = subprocess.run(
                ["git", "ls-remote", url], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0

        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
