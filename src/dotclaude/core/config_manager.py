"""Configuration management with three-tier system."""

import os
import subprocess
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from ruamel.yaml import YAML

from dotclaude.domain.constants import YAMLConfig
from dotclaude.utils.console import console


# Default configuration constants
DEFAULT_CONFIG = {
    "sync": {
        "repo_url": "git@github.com:FradSer/dotclaude.git",
        "branch": "main",
        "prefer": "remote",
    },
    "git": {
        "auto_commit": True,
        "commit_template": "sync: update configuration via dotclaude CLI",
    },
    "ui": {"use_color": True, "show_progress": True},
}


class ConfigScope(Enum):
    """Configuration scope levels."""

    LOCAL = "local"  # Project-level: ./.aicfg
    GLOBAL = "global"  # User-level: ~/.config/ai/config
    SYSTEM = "system"  # System-level: /etc/ai/config


class ConfigManager:
    """Manages configuration across three scopes following Git/npm pattern."""

    def __init__(self):
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.width = YAMLConfig.DEFAULT_WIDTH

    def get_config_path(self, scope: ConfigScope) -> Path:
        """Get the configuration file path for a given scope."""
        # Using dictionary mapping for Python 3.9+ compatibility
        scope_paths = {
            ConfigScope.LOCAL: lambda: Path.cwd() / ".aicfg",
            ConfigScope.GLOBAL: lambda: self._get_global_config_path(),
            ConfigScope.SYSTEM: lambda: Path("/etc/ai/config"),
        }

        path_func = scope_paths.get(scope)
        if path_func is None:
            raise ValueError(f"Invalid scope: {scope}")

        return path_func()

    def _get_global_config_path(self) -> Path:
        """Get the global config path, creating directory if needed."""
        config_dir = Path.home() / ".config" / "ai"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config"

    def get(self, key: str, scope: Optional[ConfigScope] = None) -> Any:
        """Get configuration value with cascading lookup."""
        # Guard clause: return early for specific scope
        if scope:
            return self._get_from_scope(key, scope)

        # Cascading lookup: local -> global -> system
        for scope_level in [ConfigScope.LOCAL, ConfigScope.GLOBAL, ConfigScope.SYSTEM]:
            if (value := self._get_from_scope(key, scope_level)) is not None:
                return value

        return None

    def set(
        self, key: str, value: Any, scope: ConfigScope = ConfigScope.GLOBAL
    ) -> None:
        """Set configuration value in specified scope."""
        config_path = self.get_config_path(scope)

        # Load existing config or create new
        config = {}
        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    config = self.yaml.load(f) or {}
            except Exception as e:
                console.print(
                    f"[warning]Failed to load config from {config_path}: {e}[/warning]"
                )

        # Set nested key (support dot notation like 'sync.branch')
        self._set_nested_value(config, key, value)

        # Write back to file
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                self.yaml.dump(config, f)
        except Exception as e:
            raise Exception(f"Failed to write config to {config_path}: {e}")

    def unset(self, key: str, scope: ConfigScope = ConfigScope.GLOBAL) -> None:
        """Remove configuration value from specified scope."""
        config_path = self.get_config_path(scope)

        if not config_path.exists():
            return

        try:
            with open(config_path, encoding="utf-8") as f:
                config = self.yaml.load(f) or {}

            # Remove nested key
            if self._unset_nested_value(config, key):
                # Write back to file
                with open(config_path, "w", encoding="utf-8") as f:
                    self.yaml.dump(config, f)

        except Exception as e:
            raise Exception(f"Failed to update config at {config_path}: {e}")

    def get_all(self, scope: ConfigScope) -> dict[str, Any]:
        """Get all configuration values from a specific scope."""
        config_path = self.get_config_path(scope)

        if not config_path.exists():
            return {}

        try:
            with open(config_path, encoding="utf-8") as f:
                return self.yaml.load(f) or {}
        except Exception as e:
            console.print(
                f"[warning]Failed to load config from {config_path}: {e}[/warning]"
            )
            return {}

    def get_all_scopes(self) -> dict[str, dict[str, Any]]:
        """Get configuration from all scopes."""
        return {scope.value: self.get_all(scope) for scope in ConfigScope}

    def edit_config(self, scope: ConfigScope) -> None:
        """Open configuration file in default editor."""
        config_path = self.get_config_path(scope)

        # Create file if it doesn't exist
        if not config_path.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.touch()

        # Get editor from environment or use default
        editor = os.environ.get("EDITOR", "nano")

        try:
            subprocess.run([editor, str(config_path)], check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to open editor: {e}")
        except FileNotFoundError:
            raise Exception(
                f"Editor '{editor}' not found. Set EDITOR environment variable."
            )

    def _get_from_scope(self, key: str, scope: ConfigScope) -> Any:
        """Get value from a specific scope."""
        config_path = self.get_config_path(scope)

        if not config_path.exists():
            return None

        try:
            with open(config_path, encoding="utf-8") as f:
                config = self.yaml.load(f) or {}

            # Support dot notation for nested keys
            return self._get_nested_value(config, key)

        except Exception:
            return None

    def _get_nested_value(self, config: dict[str, Any], key: str) -> Any:
        """Get nested value using dot notation with improved error handling."""
        try:
            from functools import reduce
            return reduce(dict.get, key.split('.'), config)
        except (AttributeError, TypeError):
            return None

    def _set_nested_value(self, config: dict[str, Any], key: str, value: Any) -> None:
        """Set nested value using dot notation."""
        keys = key.split(".")
        current = config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Set the final key
        current[keys[-1]] = value

    def _unset_nested_value(self, config: dict[str, Any], key: str) -> bool:
        """Remove nested value using dot notation. Returns True if key was found and removed."""
        keys = key.split(".")
        current = config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if not isinstance(current, dict) or k not in current:
                return False
            current = current[k]

        # Remove the final key if it exists
        if isinstance(current, dict) and keys[-1] in current:
            del current[keys[-1]]
            return True

        return False

    def get_default_config(self) -> dict[str, Any]:
        """Get default configuration values."""
        return DEFAULT_CONFIG.copy()

    def initialize_default_config(
        self, scope: ConfigScope = ConfigScope.GLOBAL
    ) -> None:
        """Initialize configuration with default values."""
        config_path = self.get_config_path(scope)

        if config_path.exists():
            console.print(f"[info]Config already exists at {config_path}[/info]")
            return

        default_config = self.get_default_config()

        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                self.yaml.dump(default_config, f)

            console.print(
                f"[success]Initialized default config at {config_path}[/success]"
            )

        except Exception as e:
            raise Exception(f"Failed to initialize config: {e}")
