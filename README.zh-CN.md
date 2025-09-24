# DotAgent CLI ![](https://img.shields.io/badge/A%20FRAD%20PRODUCT-green)

[![Twitter Follow](https://img.shields.io/twitter/follow/FradSer?style=social)](https://twitter.com/FradSer)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Configuration-blue.svg)](https://docs.anthropic.com/en/docs/claude-code)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**[English](README.md) | 中文**

> 跨不同平台管理 AI 智能体配置的通用 CLI 工具 - 目前支持 Claude Code，计划支持 GitHub Copilot、Cursor 等

DotAgent 是一个用于管理 AI 智能体配置的通用 CLI 工具。目前完全支持 Claude Code，在本地（`~/.claude/`）和远程 GitHub 仓库之间提供强大的双向同步功能。未来版本将增加对 GitHub Copilot、Cursor 和其他 AI 开发工具的支持。

## 🎯 当前支持

**Claude Code** - 完整同步支持：
- Agents、commands 和 CLAUDE.md 配置文件
- 带智能冲突解决的双向同步
- 项目特定智能体管理

## 安装

### 通过 pip 安装（推荐）
```bash
pip install dotclaude-cli
```

### 通过 uv 安装
```bash
uv tool install dotclaude-cli
```

### 开发环境安装
```bash
git clone https://github.com/FradSer/dotagent-cli.git
cd dotagent-cli
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## 设置配置仓库

使用 DotAgent 之前，你需要一个配置仓库：

1. **Fork 默认仓库**: https://github.com/FradSer/dotclaude
2. **在 fork 的仓库中自定义你的配置**
3. **同步时使用你的 fork**:
   ```bash
   dotagent claude sync --repo yourusername/dotclaude
   ```

或直接使用默认仓库：
```bash
dotagent claude sync  # 使用 github.com/FradSer/dotclaude
```

## 使用

### 基本命令

```bash
# 同步全局 Claude 配置
dotagent claude sync

# 检查同步状态
dotagent claude status

# 包含项目特定 agents
dotagent claude sync --local
```

### 仓库选项

```bash
# 使用自定义仓库
dotagent claude sync --repo user/repo

# 使用特定分支
dotagent claude sync --branch develop

# 预览变更
dotagent claude sync --dry-run

# 强制覆写冲突
dotagent claude sync --force
```

### 同步内容

**全局项目**（总是同步）：
- `~/.claude/agents/` ↔ `remote:agents/`
- `~/.claude/commands/` ↔ `remote:commands/`
- `~/.claude/CLAUDE.md` ↔ `remote:CLAUDE.md`

**项目项**（仅在使用 `--local` 时）：
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
dotagent claude sync

# 同步项目 agents
dotagent claude sync --local

# 使用自定义仓库和分支
dotagent claude sync --repo company/configs --branch main --local

# 检查将要变更的内容
dotagent claude status
dotagent claude sync --dry-run
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

- [工具仓库](https://github.com/FradSer/dotagent-cli) - 此 CLI 工具
- [默认配置仓库](https://github.com/FradSer/dotclaude) - Fork 此仓库来存储你的配置
- [问题反馈](https://github.com/FradSer/dotagent-cli/issues)
- [Claude Code 文档](https://docs.anthropic.com/claude/docs)