# DotAgent CLI ![](https://img.shields.io/badge/A%20FRAD%20PRODUCT-green)

[![Twitter Follow](https://img.shields.io/twitter/follow/FradSer?style=social)](https://twitter.com/FradSer)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Configuration-blue.svg)](https://docs.anthropic.com/en/docs/claude-code)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**English | [中文](README.zh-CN.md)**

> Universal CLI tool for managing AI agent configurations across different platforms - currently supports Claude Code with planned support for GitHub Copilot, Cursor, and more

DotAgent is a universal CLI tool for managing AI agent configurations. Currently supports Claude Code with robust bidirectional synchronization between local (`~/.claude/`) and remote GitHub repositories. Future versions will add support for GitHub Copilot, Cursor, and other AI development tools.

## 🎯 Current Support

**Claude Code** - Full synchronization support:
- Agents, commands, and CLAUDE.md configuration files
- Bidirectional sync with intelligent conflict resolution
- Project-specific agent management

## Installation

### Via pip (recommended)
```bash
pip install dotclaude-cli
```

### Via uv
```bash
uv tool install dotclaude-cli
```

### Development Installation
```bash
git clone https://github.com/FradSer/dotagent-cli.git
cd dotagent-cli
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Setup Configuration Repository

Before using DotAgent, you need a configuration repository:

1. **Fork the default repository**: https://github.com/FradSer/dotclaude
2. **Customize your configurations** in the forked repository
3. **Use your fork** when syncing:
   ```bash
   dotagent claude sync --repo yourusername/dotclaude
   ```

Or use the default repository directly:
```bash
dotagent claude sync  # Uses github.com/FradSer/dotclaude
```

## Usage

### Basic Commands

```bash
# Sync global Claude configurations
dotagent claude sync

# Check sync status
dotagent claude status

# Include project-specific agents
dotagent claude sync --local
```

### Repository Options

```bash
# Use custom repository
dotagent claude sync --repo user/repo

# Use specific branch
dotagent claude sync --branch develop

# Preview changes
dotagent claude sync --dry-run

# Force overwrite conflicts
dotagent claude sync --force
```

### What Gets Synced

**Global Items** (always synced):
- `~/.claude/agents/` ↔ `remote:agents/`
- `~/.claude/commands/` ↔ `remote:commands/`
- `~/.claude/CLAUDE.md` ↔ `remote:CLAUDE.md`

**Project Items** (only with `--local`):
- `remote:local-agents/*.md` → `.claude/agents/`

When using `--local`, you'll see a checkbox interface to select which `.md` files to copy from the remote `local-agents/` directory.

### Repository Formats

All these formats work:
- `https://github.com/user/repo`
- `git@github.com:user/repo.git`
- `user/repo`

## Examples

```bash
# Basic sync
dotagent claude sync

# Sync with project agents
dotagent claude sync --local

# Use custom repo and branch
dotagent claude sync --repo company/configs --branch main --local

# Check what would change
dotagent claude status
dotagent claude sync --dry-run
```

## Development

```bash
# Setup
uv pip install -e ".[dev]"

# Test
pytest

# Quality checks
black src tests && ruff check src tests && mypy src

# Build
uv build
```

## Requirements

- Python 3.9+
- Git
- GitHub repository with Claude Code configurations

## License

MIT License - see [LICENSE](LICENSE) file.

## Links

- [Tool Repository](https://github.com/FradSer/dotagent-cli) - This CLI tool
- [Default Config Repository](https://github.com/FradSer/dotclaude) - Fork this for your configs
- [Issues](https://github.com/FradSer/dotagent-cli/issues)
- [Claude Code Documentation](https://docs.anthropic.com/claude/docs)