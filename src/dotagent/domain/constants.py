"""Domain constants for dotclaude application."""

from pathlib import Path


class ValidationLimits:
    """Validation limits for various domain entities."""

    MAX_BRANCH_NAME_LENGTH = 250
    MAX_AGENT_NAME_LENGTH = 100
    MAX_CONFIG_KEY_LENGTH = 200
    MAX_CONFIG_VALUE_LENGTH = 1000
    MIN_AGENT_NAME_LENGTH = 3
    MIN_CONTROL_CHAR_CODE = 32


class FileExtensions:
    """File extension constants."""

    SUPPORTED_TEMPLATE_EXTENSIONS = [".md", ".yaml", ".yml", ".json"]
    AGENT_EXTENSION = ".md"
    YAML_EXTENSIONS = [".yaml", ".yml"]
    MARKDOWN_EXTENSIONS = [".md", ".markdown"]


class DefaultPaths:
    """Default path configurations."""

    CLAUDE_DIR = Path.home() / ".claude"


class DefaultRepository:
    """Default repository configuration."""

    URL = "https://github.com/FradSer/dotclaude"
    BRANCH = "main"


class SyncItems:
    """Items that are synchronized between local and remote."""

    # Global sync items: ~/.claude/ <-> remote repository
    GLOBAL_ITEMS = [
        ("agents", "dir"),
        ("commands", "dir"),
        ("CLAUDE.md", "file"),
    ]

    # Local sync items: remote -> project .claude/
    LOCAL_ITEMS = [
        ("local-agents", "dir", "agents"),  # remote/local-agents/ -> .claude/agents/
    ]

    # All items for backward compatibility
    ITEMS = GLOBAL_ITEMS + [("local-agents", "dir")]


class Git:
    """Git-related constants."""

    COMMIT_MESSAGES = {
        "sync": "sync: update configuration via dotclaude CLI",
        "bidirectional": "sync: bidirectional update via dotclaude CLI",
    }
    IGNORE_PATTERNS = [".DS_Store"]


class YAMLConfig:
    """YAML configuration constants."""

    DEFAULT_WIDTH = 4096  # Prevent line wrapping
    INDENT = 2


class Performance:
    """Performance-related constants."""

    FILE_MODIFICATION_TIME_TOLERANCE = 1.0  # seconds
    TEMP_DIR_PREFIX = "dotclaude-sync-"
    FILE_READ_BUFFER_SIZE = 4096  # bytes for chunked file reading
