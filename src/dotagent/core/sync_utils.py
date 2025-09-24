"""Utility classes for sync operations."""

import filecmp
import shutil
from pathlib import Path

from dotagent.domain.constants import Git, Performance


class SyncFileOperations:
    """Handles file and directory operations for syncing."""

    @staticmethod
    def paths_identical(path1: Path, path2: Path, is_dir: bool) -> bool:
        """Check if two paths have identical content with performance optimization."""
        try:
            if is_dir:
                return SyncFileOperations._directories_identical(path1, path2)
            else:
                return SyncFileOperations._files_identical(path1, path2)
        except (OSError, PermissionError):
            return False

    @staticmethod
    def _files_identical(path1: Path, path2: Path) -> bool:
        """Compare two files efficiently."""
        # Quick stat comparison first
        try:
            stat1, stat2 = path1.stat(), path2.stat()
            if stat1.st_size != stat2.st_size:
                return False
            # If sizes match and modification times are very close, likely identical
            if (
                abs(stat1.st_mtime - stat2.st_mtime)
                < Performance.FILE_MODIFICATION_TIME_TOLERANCE
            ):
                return True
        except OSError:
            pass

        # Full content comparison
        return filecmp.cmp(path1, path2, shallow=False)

    @staticmethod
    def _directories_identical(path1: Path, path2: Path) -> bool:
        """Compare two directories recursively."""
        dcmp = filecmp.dircmp(path1, path2)

        # Check if there are any differences
        if dcmp.left_only or dcmp.right_only or dcmp.diff_files:
            return False

        # Recursively check subdirectories
        for subdir in dcmp.common_dirs:
            if not SyncFileOperations._directories_identical(
                path1 / subdir, path2 / subdir
            ):
                return False

        return True

    @staticmethod
    def copy_path(source: Path, dest: Path, is_dir: bool) -> None:
        """Copy a file or directory."""
        if is_dir:
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(
                source, dest, ignore=shutil.ignore_patterns(*Git.IGNORE_PATTERNS)
            )
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)

    @staticmethod
    def remove_path(path: Path, is_dir: bool) -> None:
        """Remove a file or directory."""
        if not path.exists():
            return

        # Double-check if it's actually a directory to handle edge cases
        if is_dir or path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


class SyncContextManager:
    """Manages sync context initialization and cleanup."""

    def __init__(self, git_manager, repo_url: str, claude_dir: Path):
        self.git_manager = git_manager
        self.repo_url = repo_url
        self.claude_dir = claude_dir

    def initialize_context(self, branch: str) -> Path:
        """Initialize the sync context and return working directory."""
        import tempfile

        from dotagent.utils.console import console

        # Check if we're already in the dotclaude repository
        current_dir = Path.cwd()
        if self._is_dotclaude_repo(current_dir):
            console.print("[info]Using current directory as working directory[/info]")
            self.git_manager.fetch_repo(branch)
            return current_dir

        # Clone repository to temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix=Performance.TEMP_DIR_PREFIX))
        console.print(f"[info]Cloning repository to {temp_dir}[/info]")
        self.git_manager.clone_repo(self.repo_url, branch, temp_dir)
        return temp_dir

    def cleanup_context(self, working_dir: Path) -> None:
        """Clean up the sync context."""
        # Only clean up if it's a temporary directory
        if "/tmp" in str(working_dir) and Performance.TEMP_DIR_PREFIX.rstrip(
            "-"
        ) in str(working_dir):
            shutil.rmtree(working_dir, ignore_errors=True)

    def _is_dotclaude_repo(self, path: Path) -> bool:
        """Check if the given path is the target repository."""
        try:
            from git import InvalidGitRepositoryError, Repo

            # Check if it's a git repository
            git_dir = path / ".git"
            if not git_dir.exists():
                return False

            # Check if remote origin matches our target repository
            repo = Repo(path)
            if not repo.remotes:
                return False

            origin = repo.remotes.origin
            origin_url = origin.url

            # Normalize both URLs for comparison
            from dotagent.core.config_manager import ConfigManager

            config_manager = ConfigManager()
            normalized_origin = config_manager._normalize_repository_url(origin_url)
            normalized_target = config_manager._normalize_repository_url(self.repo_url)

            return normalized_origin == normalized_target

        except (Exception, InvalidGitRepositoryError):
            return False
