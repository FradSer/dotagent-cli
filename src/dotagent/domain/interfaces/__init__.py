"""Domain interfaces for dependency inversion."""

from .git_manager import GitManagerInterface
from .interactive_service import InteractiveServiceInterface

__all__ = ["GitManagerInterface", "InteractiveServiceInterface"]
