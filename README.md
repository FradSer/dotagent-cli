# DotClaude CLI

> Sync Claude Code configurations between local and remote repositories

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)

DotClaude syncs your Claude Code configurations (agents, commands, CLAUDE.md) between `~/.claude/` and GitHub repositories. By default, it syncs with [github.com/FradSer/dotclaude](https://github.com/FradSer/dotclaude), but you can specify your own repository. Project-specific agents can be selectively synced to `.claude/agents/`.

## Installation

### Via pip (recommended)
```bash
pip install dotclaude
```

### Via uv
```bash
uv tool install dotclaude
```

### Development Installation
```bash
git clone https://github.com/FradSer/dotclaude-cli.git
cd dotclaude-cli
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Setup Configuration Repository

Before using DotClaude, you need a configuration repository:

1. **Fork the default repository**: https://github.com/FradSer/dotclaude
2. **Customize your configurations** in the forked repository
3. **Use your fork** when syncing:
   ```bash
   dotclaude sync --repo yourusername/dotclaude
   ```

Or use the default repository directly:
```bash
dotclaude sync  # Uses github.com/FradSer/dotclaude
```

## Usage

### Basic Commands

```bash
# Sync global configurations
dotclaude sync

# Check sync status
dotclaude status

# Include project-specific agents
dotclaude sync --local
```

### Repository Options

```bash
# Use custom repository
dotclaude sync --repo user/repo

# Use specific branch
dotclaude sync --branch develop

# Preview changes
dotclaude sync --dry-run

# Force overwrite conflicts
dotclaude sync --force
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
dotclaude sync

# Sync with project agents
dotclaude sync --local

# Use custom repo and branch
dotclaude sync --repo company/configs --branch main --local

# Check what would change
dotclaude status
dotclaude sync --dry-run
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

- [Tool Repository](https://github.com/FradSer/dotclaude-cli) - This CLI tool
- [Default Config Repository](https://github.com/FradSer/dotclaude) - Fork this for your configs
- [Issues](https://github.com/FradSer/dotclaude-cli/issues)
- [Claude Code Documentation](https://docs.anthropic.com/claude/docs)