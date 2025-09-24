"""Global test configuration and fixtures."""

import pytest
import tempfile
from pathlib import Path
from typing import Generator

from dotagent.domain.value_objects import SyncOptions, ConflictResolution


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sync_options() -> SyncOptions:
    """Create sample sync options for testing."""
    return SyncOptions(
        conflict_resolution=ConflictResolution.REMOTE,
        branch="main",
        dry_run=False,
        force=False,
    )
