# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DotClaude is a modern CLI tool for managing Claude Code configuration with sync capabilities. It provides agent management, configuration sync, Git integration, and security validation.

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

### Development Server
```bash
# Run CLI in development mode
python -m dotclaude --help

# Or using the installed entry point
dotclaude --help
```

### Build and Package
```bash
# Build wheel
uv build

# Create standalone executable (PyInstaller)
pyinstaller build.spec
```

## Architecture

This project follows **Clean Architecture** with a strict 4-layer structure:

### Layer Structure
1. **Domain Layer** (`src/dotclaude/domain/`)
   - `entities/`: Core business entities (Agent, Repository, SyncItem)
   - `value_objects/`: Immutable value objects (AgentInfo, ConfigKey, SyncOptions, SyncResult)
   - `exceptions/`: Domain-specific exceptions
   - `constants.py`: Domain constants

2. **Use Cases Layer** (`src/dotclaude/use_cases/`)
   - `sync_use_case.py`: Main synchronization business logic
   - Orchestrates domain entities and coordinates with infrastructure

3. **Interface Adapters Layer** (`src/dotclaude/`)
   - `cli.py`: Main CLI application entry point using Typer
   - `commands/`: CLI command implementations (sync, agent, config)
   - `core/`: Application services (config_manager, sync_engine, git_manager, agent_manager)

4. **Infrastructure Layer** (`src/dotclaude/infrastructure/`)
   - `services/`: External service adapters (console, security, validation)
   - `validators/`: Input validation components
   - `error_handling/`: Error management and recovery

### Key Components
- **Sync Engine**: Handles synchronization between local and remote configurations
- **Agent Manager**: Manages AI agent configurations (global vs local)
- **Config Manager**: Handles application configuration and settings
- **Git Manager**: Provides Git integration for repository operations
- **Security Service**: Validates and sanitizes configuration data

### Design Patterns
- **Repository Pattern**: Abstract data access (`interfaces/repositories.py`)
- **Strategy Pattern**: Different sync strategies (`core/sync_strategies.py`)
- **Dependency Injection**: Clean separation of concerns
- **Error Boundary**: Centralized error handling

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
└── conftest.py         # Pytest configuration and fixtures
```

## Key Dependencies

- **Typer**: CLI framework with rich formatting support
- **GitPython**: Git operations and repository management
- **Pydantic**: Data validation and settings management
- **Rich**: Terminal formatting and console output
- **ruamel.yaml**: YAML parsing with comment preservation
- **aiofiles**: Async file operations

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