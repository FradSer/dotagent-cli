"""Error recovery mechanisms for common issues."""

import os
import time
from pathlib import Path

from ...domain.exceptions import (
    ConfigNotFoundError,
    GitOperationError,
    PermissionDeniedError,
)
from ...interfaces.services import ConsoleService


class ErrorRecovery:
    """Provides automatic recovery mechanisms for common errors."""

    # File permission constants
    FILE_READ_PERMISSIONS = 0o644
    FILE_WRITE_PERMISSIONS = 0o644
    DIR_PERMISSIONS = 0o755

    # Network retry configuration
    RETRY_DELAY_SECONDS = 2

    # Network error indicators
    NETWORK_ERROR_INDICATORS = [
        "connection",
        "timeout",
        "network",
        "dns",
        "host",
        "unreachable",
        "refused",
    ]

    def __init__(self, console_service: ConsoleService) -> None:
        """Initialize error recovery.

        Args:
            console_service: Service for console output and user interaction
        """
        self._console = console_service

    def attempt_recovery(self, exception: Exception) -> bool:
        """Attempt to recover from an exception.

        Args:
            exception: The exception to recover from

        Returns:
            True if recovery was successful, False otherwise
        """
        try:
            if isinstance(exception, ConfigNotFoundError):
                return self._recover_missing_config(exception)

            if isinstance(exception, PermissionDeniedError):
                return self._recover_permission_denied(exception)

            if isinstance(exception, GitOperationError):
                return self._recover_git_operation(exception)

            if isinstance(exception, FileNotFoundError):
                return self._recover_missing_file(exception)

            # For network-related errors, suggest retry
            if self._is_network_error(exception):
                return self._recover_network_error(exception)

            return False

        except Exception as e:
            self._console.print_error(f"Recovery attempt failed: {e}")
            return False

    def _recover_missing_config(self, error: ConfigNotFoundError) -> bool:
        """Attempt to recover from missing configuration."""
        config_key = error.details.get("config_key")
        config_path = error.details.get("config_path")

        if config_key:
            # Offer to create default configuration
            default_values = self._get_default_config_values()
            if config_key in default_values:
                default_value = default_values[config_key]

                if self._console.confirm(
                    f"Configuration '{config_key}' is missing. "
                    f"Create with default value '{default_value}'?"
                ):
                    # This would need to call the actual config service
                    # For now, just indicate that recovery would be possible
                    self._console.print(f"Would set {config_key} = {default_value}")
                    return True

        if config_path:
            # Offer to create the config file
            config_path_obj = Path(config_path)
            if self._console.confirm(
                f"Create missing configuration file at {config_path}?"
            ):
                try:
                    config_path_obj.parent.mkdir(parents=True, exist_ok=True)
                    config_path_obj.write_text("# Default configuration\n")
                    self._console.print_success(
                        f"Created configuration file: {config_path}"
                    )
                    return True
                except Exception as e:
                    self._console.print_error(f"Failed to create config file: {e}")

        return False

    def _recover_permission_denied(self, error: PermissionDeniedError) -> bool:
        """Attempt to recover from permission errors."""
        resource = error.details.get("resource")
        operation = error.details.get("operation")

        if not resource:
            return False

        resource_path = Path(resource)

        if operation == "read":
            return self._try_fix_read_permissions(resource_path)
        elif operation == "write":
            return self._try_fix_write_permissions(resource_path)

        return False

    def _try_fix_read_permissions(self, resource_path: Path) -> bool:
        """Attempt to fix read permissions for a resource."""
        if self._console.confirm(f"Try to fix read permissions for {resource_path}?"):
            try:
                os.chmod(resource_path, self.FILE_READ_PERMISSIONS)
                self._console.print_success(
                    f"Fixed read permissions for {resource_path}"
                )
                return True
            except Exception:
                self._console.print_error(
                    "Failed to fix permissions (try running with sudo)"
                )
        return False

    def _try_fix_write_permissions(self, resource_path: Path) -> bool:
        """Attempt to fix write permissions for a resource."""
        # First try to create missing directory if needed
        if self._try_create_missing_directory(resource_path):
            return True

        # Then try to fix permissions
        if self._console.confirm(f"Try to fix write permissions for {resource_path}?"):
            try:
                permissions = (
                    self.DIR_PERMISSIONS
                    if resource_path.is_dir()
                    else self.FILE_WRITE_PERMISSIONS
                )
                os.chmod(resource_path, permissions)
                self._console.print_success(
                    f"Fixed write permissions for {resource_path}"
                )
                return True
            except Exception:
                self._console.print_error(
                    "Failed to fix permissions (try running with sudo)"
                )
        return False

    def _try_create_missing_directory(self, resource_path: Path) -> bool:
        """Try to create missing parent directory."""
        if not resource_path.parent.exists():
            if self._console.confirm(
                f"Create missing directory {resource_path.parent}?"
            ):
                try:
                    resource_path.parent.mkdir(parents=True, exist_ok=True)
                    self._console.print_success(
                        f"Created directory: {resource_path.parent}"
                    )
                    return True
                except Exception:
                    pass
        return False

    def _recover_git_operation(self, error: GitOperationError) -> bool:
        """Attempt to recover from Git operation errors."""
        error_message = str(error).lower()

        # Handle authentication issues
        if "authentication" in error_message or "permission denied" in error_message:
            self._console.print("Git authentication failed. Please check:")
            self._console.print("1. SSH key is added to your Git provider")
            self._console.print("2. SSH agent is running: ssh-add -l")
            self._console.print("3. Repository URL is correct")

            if self._console.confirm("Retry the Git operation?"):
                # Would need to retry the actual operation
                return False  # Cannot actually retry here

        # Handle network issues
        if "timeout" in error_message or "connection" in error_message:
            if self._console.confirm("Git operation timed out. Retry?"):
                return False  # Cannot actually retry here

        # Handle dirty working directory
        if "dirty" in error_message or "uncommitted" in error_message:
            self._console.print("Working directory has uncommitted changes.")
            action = self._console.select(
                "How would you like to proceed?",
                ["Stash changes", "Commit changes", "Discard changes", "Cancel"],
            )

            if action.startswith("Stash"):
                self._console.print("Run: git stash")
            elif action.startswith("Commit"):
                self._console.print("Run: git add . && git commit -m 'WIP'")
            elif action.startswith("Discard"):
                self._console.print("Run: git reset --hard HEAD")

            return False  # User needs to take manual action

        return False

    def _recover_missing_file(self, error: FileNotFoundError) -> bool:
        """Attempt to recover from missing files."""
        filename = error.filename
        if not filename:
            return False

        file_path = Path(filename)

        # Offer to create missing directory
        if not file_path.parent.exists():
            if self._console.confirm(f"Create missing directory {file_path.parent}?"):
                try:
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    self._console.print_success(
                        f"Created directory: {file_path.parent}"
                    )
                    return True
                except Exception as e:
                    self._console.print_error(f"Failed to create directory: {e}")

        # For specific file types, offer to create templates
        if file_path.suffix in [".md", ".yaml", ".yml", ".json"]:
            if self._console.confirm(
                f"Create empty {file_path.suffix} file at {filename}?"
            ):
                try:
                    content = self._get_template_content(file_path.suffix)
                    file_path.write_text(content)
                    self._console.print_success(f"Created file: {filename}")
                    return True
                except Exception as e:
                    self._console.print_error(f"Failed to create file: {e}")

        return False

    def _recover_network_error(self, error: Exception) -> bool:
        """Attempt to recover from network errors."""
        if self._console.confirm("Network error detected. Retry operation?"):
            # Wait a moment before suggesting retry
            self._console.print(
                f"Waiting {self.RETRY_DELAY_SECONDS} seconds before retry..."
            )
            time.sleep(self.RETRY_DELAY_SECONDS)
            return False  # Cannot actually retry here, but indicate retry is possible

        return False

    def _is_network_error(self, exception: Exception) -> bool:
        """Check if an exception is network-related."""
        error_message = str(exception).lower()
        return any(
            indicator in error_message for indicator in self.NETWORK_ERROR_INDICATORS
        )

    def _get_default_config_values(self) -> dict[str, str]:
        """Get default configuration values for common settings."""
        return {
            "sync.branch": "main",
            "sync.prefer": "remote",
            "sync.force": "false",
            "sync.dry_run": "false",
            "git.default_branch": "main",
            "ui.interactive": "true",
        }

    def _get_template_content(self, file_extension: str) -> str:
        """Get template content for different file types."""
        templates = {
            ".md": "# Document Title\n\nContent goes here.\n",
            ".yaml": "# YAML Configuration\nkey: value\n",
            ".yml": "# YAML Configuration\nkey: value\n",
            ".json": '{\n  "key": "value"\n}\n',
        }

        return templates.get(file_extension, "")

    def suggest_manual_recovery(self, exception: Exception) -> None:
        """Suggest manual recovery steps for exceptions that can't be auto-recovered."""
        error_message = str(exception).lower()

        if "git" in error_message:
            self._console.print("Manual Git recovery steps:")
            self._console.print("1. Check repository status: git status")
            self._console.print("2. Check remote: git remote -v")
            self._console.print("3. Check authentication: ssh -T git@github.com")

        elif "permission" in error_message:
            self._console.print("Manual permission recovery steps:")
            self._console.print("1. Check file permissions: ls -la")
            self._console.print("2. Fix permissions: chmod/chown as needed")
            self._console.print("3. Run with appropriate privileges if necessary")

        elif "config" in error_message:
            self._console.print("Manual configuration recovery steps:")
            self._console.print("1. Check configuration files exist")
            self._console.print("2. Verify configuration format and values")
            self._console.print(
                "3. Initialize configuration: dotclaude config set <key> <value>"
            )
