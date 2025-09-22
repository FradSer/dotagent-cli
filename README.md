# DotClaude CLI

> Modern CLI tool for managing Claude Code configuration with sync capabilities

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)

DotClaude is a powerful command-line interface that streamlines the management of Claude Code configurations, providing seamless synchronization between local and remote repositories with robust security validation.

## 🚀 Features

- **🤖 Agent Management**: Create, configure, and manage AI agents for different projects
- **🔄 Configuration Sync**: Bidirectional sync between local and remote Claude Code configurations
- **🔗 Git Integration**: Native Git operations with repository management
- **🔒 Security Validation**: Built-in security checks and configuration validation
- **🏗️ Clean Architecture**: Domain-driven design with clear separation of concerns
- **🧪 Test Coverage**: Comprehensive test suite with TDD approach

## 📦 Installation

### From PyPI (when published)
```bash
pip install dotclaude
```

### Development Installation
```bash
# Clone the repository
git clone https://github.com/FradSer/dotclaude.git
cd dotclaude

# Install with uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

## 🛠️ Usage

### Basic Commands

```bash
# Show help
dotclaude --help

# Sync configuration with repository
dotclaude sync

# Manage AI agents
dotclaude agent list
dotclaude agent create --name "my-agent" --type local

# Configure settings
dotclaude config set key value
dotclaude config get key
```

### Sync Operations

```bash
# Sync from remote to local
dotclaude sync pull

# Sync from local to remote
dotclaude sync push

# Two-way sync with conflict resolution
dotclaude sync bidirectional
```

### Agent Management

```bash
# List all agents
dotclaude agent list

# Create a new agent
dotclaude agent create --name "project-agent" --type local

# Update agent configuration
dotclaude agent update "project-agent" --config config.yaml

# Remove an agent
dotclaude agent remove "project-agent"
```

## 🏗️ Architecture

DotClaude follows Clean Architecture principles with four distinct layers:

- **Domain Layer**: Core business entities and rules
- **Use Cases Layer**: Application business logic
- **Interface Adapters**: CLI commands and external interfaces
- **Infrastructure Layer**: External services and data persistence

## 🧪 Development

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup Development Environment

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=dotclaude --cov-report=html

# Format code
black src tests

# Lint code
ruff check src tests

# Type checking
mypy src
```

### Building

```bash
# Build wheel
uv build

# Create standalone executable
pyinstaller build.spec
```

## 📋 Requirements

- Python 3.9 or higher
- Git (for repository operations)
- Dependencies managed via `uv.lock`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the project's coding standards:
- Use conventional commit messages
- Maintain test coverage above 80%
- Follow TDD practices
- Run all quality checks before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/FradSer/dotclaude)
- [Issue Tracker](https://github.com/FradSer/dotclaude/issues)
- [Claude Code Documentation](https://docs.anthropic.com/claude/docs)