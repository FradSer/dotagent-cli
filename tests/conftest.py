"""Global test configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import Mock, MagicMock

from dotagent.domain.entities import SyncItem, Agent, Repository
from dotagent.domain.entities.sync_item import SyncItemType
from dotagent.domain.entities.agent import AgentType
from dotagent.domain.value_objects import SyncOptions, ConflictResolution
from dotagent.interfaces.repositories import (
    SyncRepository,
    AgentRepository,
    ConfigRepository,
    GitRepository,
    FileSystemRepository,
)
from dotagent.interfaces.services import (
    ConsoleService,
    ValidationService,
    SecurityService,
)


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_sync_item(temp_dir: Path) -> SyncItem:
    """Create a sample sync item for testing."""
    local_path = temp_dir / "local" / "test.md"
    remote_path = temp_dir / "remote" / "test.md"

    # Create the local file
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text("# Test Content\n\nThis is a test file.")

    return SyncItem(
        name="test.md",
        item_type=SyncItemType.FILE,
        local_path=local_path,
        remote_path=remote_path,
    )


@pytest.fixture
def sample_agent(temp_dir: Path) -> Agent:
    """Create a sample agent for testing."""
    agent_path = temp_dir / "agents" / "test-agent.yaml"
    agent_path.parent.mkdir(parents=True, exist_ok=True)
    agent_path.write_text(
        """
name: test-agent
description: A test agent for unit testing
specializations:
  - testing
  - validation
""".strip()
    )

    return Agent(
        name="test-agent",
        agent_type=AgentType.LOCAL,
        path=agent_path,
        description="A test agent for unit testing",
        specializations=["testing", "validation"],
    )


@pytest.fixture
def sample_repository() -> Repository:
    """Create a sample repository for testing."""
    return Repository(
        url="https://github.com/test/repo.git",
        branch="main",
    )


@pytest.fixture
def sync_options() -> SyncOptions:
    """Create sample sync options for testing."""
    return SyncOptions(
        conflict_resolution=ConflictResolution.REMOTE,
        branch="main",
        dry_run=False,
        force=False,
    )


@pytest.fixture
def mock_sync_repository() -> Mock:
    """Mock sync repository."""
    mock = Mock(spec=SyncRepository)
    mock.get_sync_items.return_value = []
    mock.get_sync_item.return_value = None
    mock.copy_item.return_value = True
    mock.delete_item.return_value = True
    return mock


@pytest.fixture
def mock_agent_repository() -> Mock:
    """Mock agent repository."""
    mock = Mock(spec=AgentRepository)
    mock.get_all_agents.return_value = []
    mock.get_local_agents.return_value = []
    mock.get_global_agents.return_value = []
    mock.get_agent.return_value = None
    mock.copy_agent.return_value = True
    mock.save_agent.return_value = True
    mock.delete_agent.return_value = True
    return mock


@pytest.fixture
def mock_config_repository() -> Mock:
    """Mock configuration repository."""
    mock = Mock(spec=ConfigRepository)
    mock.get_config.return_value = None
    mock.get_all_config.return_value = {}
    mock.get_config_path.return_value = Path("/tmp/config")
    return mock


@pytest.fixture
def mock_git_repository() -> Mock:
    """Mock Git repository."""
    mock = Mock(spec=GitRepository)
    mock.clone.return_value = True
    mock.fetch.return_value = True
    mock.pull.return_value = True
    mock.push.return_value = True
    mock.get_current_branch.return_value = "main"
    mock.switch_branch.return_value = True
    mock.is_clean.return_value = True
    mock.get_status.return_value = {"clean": True}
    return mock


@pytest.fixture
def mock_filesystem_repository() -> Mock:
    """Mock filesystem repository."""
    mock = Mock(spec=FileSystemRepository)
    mock.copy_file.return_value = True
    mock.copy_directory.return_value = True
    mock.delete_file.return_value = True
    mock.delete_directory.return_value = True
    mock.create_directory.return_value = True
    mock.exists.return_value = True
    mock.is_file.return_value = True
    mock.is_directory.return_value = False
    mock.get_size.return_value = 1024
    mock.compare_files.return_value = True
    mock.compare_directories.return_value = {"same": True}
    return mock


@pytest.fixture
def mock_console_service() -> Mock:
    """Mock console service."""
    mock = Mock(spec=ConsoleService)
    mock.confirm.return_value = True
    mock.prompt.return_value = "test"
    mock.select.return_value = "option1"
    return mock


@pytest.fixture
def mock_validation_service() -> Mock:
    """Mock validation service."""
    mock = Mock(spec=ValidationService)
    mock.validate_path.return_value = Path("/safe/path")
    mock.validate_url.return_value = "https://safe.url"
    mock.validate_branch_name.return_value = "safe-branch"
    mock.validate_agent_name.return_value = "safe-agent"
    mock.validate_config_key.return_value = "safe.key"
    mock.validate_config_value.return_value = "safe_value"
    return mock


@pytest.fixture
def mock_security_service() -> Mock:
    """Mock security service."""
    mock = Mock(spec=SecurityService)
    mock.is_safe_path.return_value = True
    mock.sanitize_path.return_value = Path("/safe/path")
    mock.is_safe_url.return_value = True
    mock.sanitize_filename.return_value = "safe_filename"
    mock.check_permissions.return_value = True
    mock.mask_sensitive_data.return_value = "masked_data"
    return mock


@pytest.fixture
def all_mocks(
    mock_sync_repository: Mock,
    mock_agent_repository: Mock,
    mock_config_repository: Mock,
    mock_git_repository: Mock,
    mock_filesystem_repository: Mock,
    mock_console_service: Mock,
    mock_validation_service: Mock,
    mock_security_service: Mock,
) -> Dict[str, Mock]:
    """Convenience fixture providing all mocks."""
    return {
        "sync_repository": mock_sync_repository,
        "agent_repository": mock_agent_repository,
        "config_repository": mock_config_repository,
        "git_repository": mock_git_repository,
        "filesystem_repository": mock_filesystem_repository,
        "console_service": mock_console_service,
        "validation_service": mock_validation_service,
        "security_service": mock_security_service,
    }


@pytest.fixture(autouse=True)
def reset_mocks(all_mocks: Dict[str, Mock]) -> None:
    """Automatically reset all mocks before each test."""
    for mock in all_mocks.values():
        mock.reset_mock()


class TestFixtures:
    """Helper class for creating test data."""

    @staticmethod
    def create_sync_items(temp_dir: Path, count: int = 3) -> list[SyncItem]:
        """Create multiple sync items for testing."""
        items = []
        for i in range(count):
            local_path = temp_dir / "local" / f"item_{i}.md"
            remote_path = temp_dir / "remote" / f"item_{i}.md"

            local_path.parent.mkdir(parents=True, exist_ok=True)
            remote_path.parent.mkdir(parents=True, exist_ok=True)

            local_path.write_text(f"# Item {i}\n\nContent for item {i}")
            remote_path.write_text(f"# Item {i}\n\nDifferent content for item {i}")

            items.append(
                SyncItem(
                    name=f"item_{i}.md",
                    item_type=SyncItemType.FILE,
                    local_path=local_path,
                    remote_path=remote_path,
                )
            )
        return items

    @staticmethod
    def create_agents(temp_dir: Path, count: int = 3) -> list[Agent]:
        """Create multiple agents for testing."""
        agents = []
        for i in range(count):
            agent_path = temp_dir / "agents" / f"agent-{i}.yaml"
            agent_path.parent.mkdir(parents=True, exist_ok=True)
            agent_path.write_text(
                f"""
name: agent-{i}
description: Test agent {i}
specializations:
  - test
  - automation
""".strip()
            )

            agents.append(
                Agent(
                    name=f"agent-{i}",
                    agent_type=AgentType.LOCAL,
                    path=agent_path,
                    description=f"Test agent {i}",
                    specializations=["test", "automation"],
                )
            )
        return agents
