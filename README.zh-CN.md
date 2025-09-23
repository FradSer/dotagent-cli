# DotClaude CLI

> 在本地和远程仓库之间同步 Claude Code 配置

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)

DotClaude 在 `~/.claude/` 和 GitHub 仓库之间同步你的 Claude Code 配置（agents、commands、CLAUDE.md）。默认同步 [github.com/FradSer/dotclaude](https://github.com/FradSer/dotclaude)，但你可以指定自己的仓库。项目特定的 agents 可以选择性地同步到 `.claude/agents/`。

## 安装

### 通过 Homebrew 安装（推荐）
```bash
brew install https://raw.githubusercontent.com/FradSer/dotclaude-cli/main/Formula/dotclaude.rb
```

### 通过 pip 安装
```bash
pip install dotclaude
```

### 开发环境安装
```bash
git clone https://github.com/FradSer/dotclaude-cli.git
cd dotclaude-cli
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## 设置配置仓库

使用 DotClaude 之前，你需要一个配置仓库：

1. **Fork 默认仓库**: https://github.com/FradSer/dotclaude
2. **在 fork 的仓库中自定义你的配置**
3. **同步时使用你的 fork**:
   ```bash
   dotclaude sync --repo yourusername/dotclaude
   ```

或直接使用默认仓库：
```bash
dotclaude sync  # 使用 github.com/FradSer/dotclaude
```

## 使用

### 基本命令

```bash
# 同步全局配置
dotclaude sync

# 检查同步状态
dotclaude status

# 包含项目特定 agents
dotclaude sync --local
```

### 仓库选项

```bash
# 使用自定义仓库
dotclaude sync --repo user/repo

# 使用特定分支
dotclaude sync --branch develop

# 预览变更
dotclaude sync --dry-run

# 强制覆写冲突
dotclaude sync --force
```

### 同步内容

**全局项目**（总是同步）：
- `~/.claude/agents/` ↔ `remote:agents/`
- `~/.claude/commands/` ↔ `remote:commands/`
- `~/.claude/CLAUDE.md` ↔ `remote:CLAUDE.md`

**项目项目**（仅在使用 `--local` 时）：
- `remote:local-agents/*.md` → `.claude/agents/`

使用 `--local` 时，你会看到一个复选框界面来选择从远程 `local-agents/` 目录复制哪些 `.md` 文件。

### 仓库格式

支持以下格式：
- `https://github.com/user/repo`
- `git@github.com:user/repo.git`
- `user/repo`

## 示例

```bash
# 基础同步
dotclaude sync

# 同步项目 agents
dotclaude sync --local

# 使用自定义仓库和分支
dotclaude sync --repo company/configs --branch main --local

# 检查将要变更的内容
dotclaude status
dotclaude sync --dry-run
```

## 开发

```bash
# 设置
uv pip install -e ".[dev]"

# 测试
pytest

# 质量检查
black src tests && ruff check src tests && mypy src

# 构建
uv build
```

## 要求

- Python 3.9+
- Git
- 包含 Claude Code 配置的 GitHub 仓库

## 许可证

MIT 许可证 - 查看 [LICENSE](LICENSE) 文件。

## 链接

- [工具仓库](https://github.com/FradSer/dotclaude-cli) - 此 CLI 工具
- [默认配置仓库](https://github.com/FradSer/dotclaude) - Fork 此仓库来存储你的配置
- [问题反馈](https://github.com/FradSer/dotclaude-cli/issues)
- [Claude Code 文档](https://docs.anthropic.com/claude/docs)