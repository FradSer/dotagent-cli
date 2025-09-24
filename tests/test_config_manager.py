"""Test configuration manager."""

import tempfile
from pathlib import Path

import pytest

from dotagent.core.config_manager import ConfigManager, ConfigScope


@pytest.fixture
def temp_config_dir():
    """Create temporary directory for config tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def test_config_scope_enum():
    """Test ConfigScope enum values."""
    assert ConfigScope.LOCAL.value == "local"
    assert ConfigScope.GLOBAL.value == "global"
    assert ConfigScope.SYSTEM.value == "system"


def test_config_manager_init():
    """Test ConfigManager initialization."""
    manager = ConfigManager()
    assert manager.yaml is not None


def test_get_nested_value():
    """Test getting nested configuration values."""
    manager = ConfigManager()
    config = {
        "sync": {"branch": "main", "repo_url": "https://github.com/test/repo.git"},
        "simple_key": "simple_value",
    }

    assert manager._get_nested_value(config, "simple_key") == "simple_value"
    assert manager._get_nested_value(config, "sync.branch") == "main"
    assert (
        manager._get_nested_value(config, "sync.repo_url")
        == "https://github.com/test/repo.git"
    )
    assert manager._get_nested_value(config, "nonexistent.key") is None


def test_set_nested_value():
    """Test setting nested configuration values."""
    manager = ConfigManager()
    config = {}

    manager._set_nested_value(config, "simple_key", "simple_value")
    assert config["simple_key"] == "simple_value"

    manager._set_nested_value(config, "sync.branch", "develop")
    assert config["sync"]["branch"] == "develop"

    manager._set_nested_value(
        config, "sync.repo_url", "https://github.com/test/repo.git"
    )
    assert config["sync"]["repo_url"] == "https://github.com/test/repo.git"


def test_unset_nested_value():
    """Test removing nested configuration values."""
    manager = ConfigManager()
    config = {
        "sync": {"branch": "main", "repo_url": "https://github.com/test/repo.git"},
        "simple_key": "simple_value",
    }

    # Remove simple key
    assert manager._unset_nested_value(config, "simple_key") is True
    assert "simple_key" not in config

    # Remove nested key
    assert manager._unset_nested_value(config, "sync.branch") is True
    assert "branch" not in config["sync"]
    assert "repo_url" in config["sync"]  # Other key should remain

    # Try to remove non-existent key
    assert manager._unset_nested_value(config, "nonexistent.key") is False


def test_get_default_config():
    """Test default configuration values."""
    manager = ConfigManager()
    default_config = manager.get_default_config()

    assert "sync" in default_config
    assert "git" in default_config
    assert "ui" in default_config
    assert default_config["sync"]["branch"] == "main"
