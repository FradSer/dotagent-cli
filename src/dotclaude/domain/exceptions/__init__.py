"""Domain exceptions for dotclaude application."""

from .base import DotClaudeError
from .config import ConfigNotFoundError, ConfigurationError, InvalidConfigError
from .git import BranchNotFoundError, GitOperationError, RepositoryNotFoundError
from .security import InvalidPathError, PathTraversalError, SecurityError
from .sync import ConflictResolutionError, SyncError, SyncValidationError

__all__ = [
    "DotClaudeError",
    "ConfigurationError",
    "ConfigNotFoundError",
    "InvalidConfigError",
    "GitOperationError",
    "RepositoryNotFoundError",
    "BranchNotFoundError",
    "SyncError",
    "ConflictResolutionError",
    "SyncValidationError",
    "SecurityError",
    "PathTraversalError",
    "InvalidPathError",
]
