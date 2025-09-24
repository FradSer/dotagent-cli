"""Test the main CLI application."""

import pytest
from typer.testing import CliRunner

from dotagent.cli import app


def test_cli_version():
    """Test version flag."""
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "dotagent version" in result.stdout


def test_cli_help():
    """Test help output."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "dotagent" in result.stdout
    assert "claude" in result.stdout


def test_claude_sync_help():
    """Test claude sync command help."""
    runner = CliRunner()
    result = runner.invoke(app, ["claude", "sync", "--help"])
    assert result.exit_code == 0
    assert "Sync configuration" in result.stdout


def test_claude_status_help():
    """Test claude status command help."""
    runner = CliRunner()
    result = runner.invoke(app, ["claude", "status", "--help"])
    assert result.exit_code == 0
    assert "Show sync status" in result.stdout
