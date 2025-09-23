# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DotClaude is a modern CLI tool for managing Claude Code configuration with sync capabilities. It provides a simplified, focused interface for synchronizing configurations between local and remote repositories.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment using uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m slow          # Slow tests only

# Run single test file
pytest tests/test_cli.py

# Run with verbose output
pytest -v
```

### Code Quality
```bash
# Format code
black src tests

# Lint code
ruff check src tests

# Type checking
mypy src

# Run all quality checks
black src tests && ruff check src tests && mypy src
```

### Development and Testing
```bash
# Run CLI in development mode
uv run dotclaude --help

# Test core commands
uv run dotclaude status
uv run dotclaude sync --dry-run
uv run dotclaude status --branch develop

# Test with custom repository
uv run dotclaude sync --repo user/repo --dry-run
uv run dotclaude status --repo https://github.com/user/repo.git

# Test with local agents
uv run dotclaude sync --local --dry-run
uv run dotclaude sync --local --force

# Test conflict resolution (create local differences first)
echo "# Local test" > ~/.claude/CLAUDE.md
uv run dotclaude sync --branch develop

# Test combined flags
uv run dotclaude sync --local --branch develop --repo user/repo
```

### Build and Package
```bash
# Build wheel
uv build

# Create standalone executable (PyInstaller)
pyinstaller build.spec
```

## CLI Architecture

The CLI has been simplified to focus on core sync functionality with only **two main commands**:

### Command Structure
```bash
dotclaude sync     # Interactive sync with conflict resolution
dotclaude status   # Show sync status and differences
```

### Unified Global Flags
All commands support these consistent flags:
- `--dry-run` - Preview changes without applying (sync command)
- `--force` - Force overwrite without prompts (sync command)
- `--branch <name>` - Use specific branch (default: main)
- `--repo <url>` - Repository URL (HTTPS, SSH, or user/repo format)
- `--local` - Include project-specific agents in sync (sync command)

### Important CLI Notes
- The CLI uses **bidirectional sync** by default with interactive conflict resolution
- When `--force` is used, conflicts are resolved in favor of remote (overwrites local)
- Status command displays separated tables for global vs local configuration items
- **Local-agents processing requires explicit opt-in** via `--local` flag
- Without `--local`, only global items (agents, commands, CLAUDE.md) are processed
- Local-agents provide interactive file selection (space to select .md files)

## Architecture

This project follows **Clean Architecture** with a simplified structure focused on sync operations:

### Core Architecture Layers

1. **Domain Layer** (`src/dotclaude/domain/`)
   - `value_objects/`: Immutable objects (SyncOptions, SyncResult, ConflictResolution)
   - `exceptions/`: Domain-specific exceptions
   - `constants.py`: Sync items and configuration constants

2. **Use Cases Layer** (`src/dotclaude/use_cases/`)
   - `sync_use_case.py`: Main synchronization business logic
   - Orchestrates domain entities and coordinates with infrastructure

3. **Application Layer** (`src/dotclaude/`)
   - `cli.py`: **Single consolidated CLI file** containing all commands
   - `core/`: Application services (sync_engine, git_manager, config_manager)

4. **Infrastructure Layer** (`src/dotclaude/infrastructure/`)
   - `error_handling/`: Error management and user-friendly formatting
   - `services/`: External service adapters

### Key Components

- **Sync Engine**: Handles synchronization using strategy pattern
- **Sync Strategies**: Different approaches (pull-only, push-only, bidirectional)
- **Git Manager**: Repository operations and branch management
- **Config Manager**: Application configuration with cascading scopes
- **Interactive Conflict Resolution**: Uses inquirer for user-friendly conflict handling
- **LocalAgentsService**: Handles interactive file selection for project-specific agents

### Sync Flow Architecture

The sync process follows this pattern:
1. **CLI** parses commands and creates `SyncOptions` (including `include_local_agents` flag)
2. **SyncEngine** determines strategy based on options
3. **Strategy** filters sync items based on `--local` flag
4. **Global items** are always processed with conflict resolution prompts
5. **Local-agents** (when enabled) shows interactive file selection for .md files
6. **Git operations** commit and push changes when needed

### Sync Items Configuration

Two types of sync items are handled differently:
- **Global items**: `agents`, `commands`, `CLAUDE.md` (always processed, synced with `~/.claude/`)
- **Local items**: `local-agents` (only when `--local` flag is used, remote → project `.claude/agents/`)

#### Local-Agents File Selection Behavior
- Scans remote `local-agents/` directory for `.md` files
- Presents interactive checkbox interface for file selection
- Files are not pre-selected (user must actively choose with spacebar)
- Selected files are copied to project's `.claude/agents/` directory
- `--force` flag bypasses selection and copies all available `.md` files

### Two-Tier Interaction Model

The CLI implements a sophisticated two-tier interaction system:

1. **Global Items Conflict Resolution**: When local and remote versions differ
   - Shows interactive choice: "Use local", "Use remote", or "Skip"
   - Uses arrow keys for navigation, Enter to confirm
   - Applies to `agents`, `commands`, `CLAUDE.md`

2. **Local-Agents File Selection**: When `--local` flag is enabled
   - Shows checkbox interface for individual `.md` file selection
   - Uses spacebar to select/deselect, Enter to confirm
   - No files are pre-selected (explicit user choice required)

## Testing Strategy

The project uses **Test-Driven Development (TDD)** with comprehensive test coverage:

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
- **Integration Tests** (`tests/integration/`): Test component interactions
- **Domain Tests**: Focused on business logic validation
- **Use Case Tests**: End-to-end business scenarios

### Test Organization
```
tests/
├── unit/
│   ├── domain/          # Domain entity tests
│   ├── use_cases/       # Business logic tests
│   └── infrastructure/  # Infrastructure tests
├── integration/         # Integration tests
├── fixtures/            # Test fixtures and data
├── conftest.py         # Pytest configuration and fixtures
├── test_cli.py         # CLI integration tests
└── test_config_manager.py  # Configuration management tests
```

## Key Dependencies

- **Typer**: CLI framework with rich formatting support
- **GitPython**: Git operations and repository management
- **Pydantic**: Data validation and settings management
- **Rich**: Terminal formatting and console output
- **ruamel.yaml**: YAML parsing with comment preservation
- **aiofiles**: Async file operations
- **inquirer**: Interactive prompts for conflict resolution and file selection

## Configuration

- **pyproject.toml**: Project configuration, dependencies, and tool settings
- **uv.lock**: Locked dependency versions for reproducible builds
- **build.spec**: PyInstaller configuration for standalone executables
- Coverage target: 80% minimum coverage required
- Python 3.9+ required

## Security Considerations

- All configuration data is validated before processing
- Path traversal protection for file operations
- Git operations are sandboxed to repository boundaries
- Sensitive data is never logged or exposed in error messages