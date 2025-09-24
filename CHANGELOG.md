# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-09-24

### Added

- Clean Architecture implementation with 4-layer structure
- Domain layer with entities, value objects, and exceptions
- Use Cases layer for business logic orchestration
- Application layer for core services
- Infrastructure layer for external service adapters
- Dependency inversion with interfaces for GitManager and InteractiveService
- Strategy pattern implementation for sync operations
- SyncUseCase for centralized business logic
- Domain-specific exceptions for better error handling
- Immutable value objects for SyncOptions and SyncResult

### Changed

- Refactored core components to follow Clean Architecture principles
- Moved sync strategies to domain layer
- Extracted business logic into use cases
- Improved separation of concerns
- Updated import structure to follow dependency rule
- Restored inquirer with arrow key navigation support

### Fixed

- Circular import issues by moving StrategyFactory to use cases layer
- Module organization for better maintainability

## [0.1.3] - 2025-09-24

### Fixed

- Project naming consistency throughout all configuration files
- Email address updated from frad@frad.io to fradser@gmail.com
- Package name unified to dotagent-cli across all documentation
- Installation instructions corrected in README files

## [0.1.2] - 2025-09-24

### Added

- FRAD PRODUCT branding badges in README files
- Twitter Follow badge for social media presence
- Claude Code Configuration badge
- Language switcher between English and Chinese documentation
- Comprehensive changelog following Keep a Changelog format

### Changed

- Updated package name from `dotagent` to `dotagent-cli` for PyPI publication
- Rebranded to "Universal AI Agent Configuration Tool"
- Updated repository URLs to match renamed GitHub repository (`dotagent-cli`)
- Updated FRAD PRODUCT badge color to green

### Removed

- Outdated GitHub Actions release workflow with incorrect package references

## [0.1.1] - 2025-09-24

### Fixed

- Corrected version number from 2.0.0 to 0.1.1 in multiple configuration files
- Updated imports and references for dotagent package structure

### Changed

- Prioritized pip installation over Homebrew in documentation
- Updated uv.lock to reflect correct version numbers

### Removed

- Homebrew formula support in favor of PyPI distribution
- Back-merged main branch changes to develop after release

## [0.1.0] - 2025-09-24

### Added

- Core DotAgent CLI implementation with sync and status commands
- Interactive conflict resolution for configuration synchronization
- Support for `--local` parameter for selective local-agents processing
- Branch support in status command for repository management
- Bidirectional synchronization between local (`~/.claude/`) and remote repositories
- Local-agents sync functionality for project-specific configurations
- Homebrew installation support with formula and release workflow
- Comprehensive project documentation and Claude Code guidance
- Strategy factory pattern for sync operations
- Interactive UI for conflict resolution during sync
- Support for multiple repository formats (HTTPS, SSH, user/repo)

### Changed

- Simplified CLI structure to focus on sync and status commands only
- Improved sync functionality with better error handling
- Extracted common sync command helpers for better code organization
- Enhanced README with comprehensive project information
- Refactored codebase to eliminate code duplication
- Improved configuration and agent manager code quality

### Fixed

- Resolved TypeError issues with --help command
- Fixed directory handling bugs in sync operations
- Prevented sync operations from hanging with better error handling
- Corrected Typer boolean flag syntax and parameter parsing
- Improved bidirectional sync git operation logic
- Fixed linting issues and import ordering

### Removed

- Emoji usage in CLI output for better terminal compatibility
- Problematic is_flag option from Typer configuration
- Magic numbers replaced with named constants

[unreleased]: https://github.com/FradSer/dotagent-cli/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/FradSer/dotagent-cli/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/FradSer/dotagent-cli/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/FradSer/dotagent-cli/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/FradSer/dotagent-cli/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/FradSer/dotagent-cli/releases/tag/v0.1.0