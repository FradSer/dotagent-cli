"""Test the main CLI application."""

import pytest
from typer.testing import CliRunner

from dotagent.cli import app


def test_cli_version():
    """Test version flag."""
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "dotclaude version" in result.stdout


def test_cli_help():
    """Test help output."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "dotclaude" in result.stdout
    assert "Sync configuration" in result.stdout


def test_sync_help():
    """Test sync command help."""
    runner = CliRunner()
    result = runner.invoke(app, ["sync", "--help"])
    assert result.exit_code == 0
    assert "Sync configuration" in result.stdout


def test_agent_help():
    """Test agent command help."""
    runner = CliRunner()
    result = runner.invoke(app, ["agent", "--help"])
    assert result.exit_code == 0
    assert "Manage AI agents" in result.stdout


def test_config_help():
    """Test config command help."""
    runner = CliRunner()
    result = runner.invoke(app, ["config", "--help"])
    assert result.exit_code == 0
    assert "Manage configuration" in result.stdout
