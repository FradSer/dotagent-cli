"""Interfaces (ports) for dotclaude application.

These interfaces define the contracts between different layers of the application,
following the Dependency Inversion Principle from SOLID.
"""

from .repositories import (
    AgentRepository,
    ConfigRepository,
    FileSystemRepository,
    GitRepository,
    SyncRepository,
)
from .services import (
    ConsoleService,
    SecurityService,
    ValidationService,
)

__all__ = [
    "SyncRepository",
    "AgentRepository",
    "ConfigRepository",
    "GitRepository",
    "FileSystemRepository",
    "ConsoleService",
    "ValidationService",
    "SecurityService",
]
