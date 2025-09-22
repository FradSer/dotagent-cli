"""Agent information value object."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AgentInfo:
    """Value object containing agent information."""

    name: str
    description: Optional[str] = None
    specializations: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    size: Optional[int] = None
    exists: bool = False
