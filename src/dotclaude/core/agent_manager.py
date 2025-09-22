"""Agent management functionality."""

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import typer
from rich.prompt import Confirm, IntPrompt
from rich.table import Table

from dotclaude.utils.console import console


@dataclass
class AgentInfo:
    """Information about an agent."""

    name: str
    type: str  # "global" or "local"
    path: Path
    description: str
    specializations: list[str]


@dataclass
class CopyResult:
    """Result of copying agents."""

    success: bool
    copied_count: int = 0
    skipped_count: int = 0
    error: Optional[str] = None


class AgentManager:
    """Manages AI agents for dotclaude."""

    def __init__(self):
        self.claude_dir = Path.home() / ".claude"
        self.global_agents_dir = self.claude_dir / "agents"
        self.local_agents_dir = Path.cwd() / "local-agents"
        self.project_agents_dir = Path.cwd() / ".claude" / "agents"

    def list_global_agents(self) -> list[AgentInfo]:
        """List all global agents."""
        agents = []
        if self.global_agents_dir.exists():
            for agent_file in self.global_agents_dir.glob("*.md"):
                agents.append(self._parse_agent_file(agent_file, "global"))
        return agents

    def list_local_agents(self) -> list[AgentInfo]:
        """List all local agents."""
        agents = []
        if self.local_agents_dir.exists():
            for agent_file in self.local_agents_dir.glob("*.md"):
                agents.append(self._parse_agent_file(agent_file, "local"))
        return agents

    def list_all_agents(self) -> list[AgentInfo]:
        """List all agents (global and local)."""
        return self.list_global_agents() + self.list_local_agents()

    def get_agent_info(self, name: str) -> Optional[AgentInfo]:
        """Get detailed information about a specific agent."""
        # Check global agents first
        for agent in self.list_global_agents():
            if agent.name == name or agent.name == f"{name}.md":
                return agent

        # Then check local agents
        for agent in self.list_local_agents():
            if agent.name == name or agent.name == f"{name}.md":
                return agent

        return None

    def copy_agents(self, agent_names: list[str], force: bool = False) -> CopyResult:
        """Copy specified agents to project directory."""
        if not self.local_agents_dir.exists():
            return CopyResult(success=False, error="No local-agents directory found")

        copied_count = 0
        skipped_count = 0
        self.project_agents_dir.mkdir(parents=True, exist_ok=True)

        for agent_name in agent_names:
            result = self._copy_single_agent(agent_name, force)
            if result == "copied":
                copied_count += 1
            elif result == "skipped":
                skipped_count += 1

        return CopyResult(
            success=True, copied_count=copied_count, skipped_count=skipped_count
        )

    def _copy_single_agent(self, agent_name: str, force: bool) -> str:
        """Copy a single agent and return the result status."""
        # Ensure .md extension
        if not agent_name.endswith(".md"):
            agent_name = f"{agent_name}.md"

        source_file = self.local_agents_dir / agent_name
        dest_file = self.project_agents_dir / agent_name

        if not source_file.exists():
            console.print(f"[warning]Agent not found: {agent_name}[/warning]")
            return "not_found"

        if dest_file.exists() and not force:
            if self._files_identical(source_file, dest_file):
                console.print(f"[info]Agent already up to date: {agent_name}[/info]")
                return "skipped"
            else:
                overwrite = Confirm.ask(f"Agent {agent_name} exists. Overwrite?")
                if not overwrite:
                    console.print(f"[info]Skipping: {agent_name}[/info]")
                    return "skipped"

        # Copy the agent
        shutil.copy2(source_file, dest_file)
        console.print(f"[success]Copied agent: {agent_name}[/success]")
        return "copied"

    def copy_all_local_agents(self, force: bool = False) -> CopyResult:
        """Copy all local agents to project directory."""
        if not self.local_agents_dir.exists():
            return CopyResult(success=False, error="No local-agents directory found")

        agent_files = list(self.local_agents_dir.glob("*.md"))
        if not agent_files:
            return CopyResult(
                success=False, error="No agents found in local-agents directory"
            )

        agent_names = [f.name for f in agent_files]
        return self.copy_agents(agent_names, force=force)

    def copy_agents_interactive(self, force: bool = False) -> CopyResult:
        """Interactive agent selection and copying."""
        local_agents = self.list_local_agents()

        if not local_agents:
            console.print("[warning]No local agents found[/warning]")
            return CopyResult(success=False, error="No local agents found")

        self._display_agent_selection_table(local_agents)
        return self._handle_user_agent_selection(local_agents, force)

    def _display_agent_selection_table(self, local_agents: list[AgentInfo]) -> None:
        """Display a table of available agents for selection."""
        table = Table(
            title="Available Local Agents",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Index", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Description", style="white")

        for i, agent in enumerate(local_agents, 1):
            table.add_row(str(i), agent.name.replace(".md", ""), agent.description)

        console.print(table)
        console.print(f"[cyan]{len(local_agents) + 1})[/cyan] Copy all agents")
        console.print(f"[cyan]{len(local_agents) + 2})[/cyan] Cancel")

    def _handle_user_agent_selection(
        self, local_agents: list[AgentInfo], force: bool
    ) -> CopyResult:
        """Handle user selection and execute the appropriate action."""
        while True:
            try:
                choice = IntPrompt.ask(
                    "Select agent(s) to copy",
                    default=len(local_agents) + 2,
                    show_default=True,
                )

                if choice == len(local_agents) + 2:  # Cancel
                    console.print("[info]Cancelled[/info]")
                    return CopyResult(success=True, copied_count=0)

                elif choice == len(local_agents) + 1:  # Copy all
                    return self.copy_all_local_agents(force=force)

                elif 1 <= choice <= len(local_agents):  # Copy specific agent
                    selected_agent = local_agents[choice - 1]
                    return self.copy_agents([selected_agent.name], force=force)

                else:
                    console.print("[error]Invalid choice. Please try again.[/error]")

            except (ValueError, typer.Abort):
                console.print("[info]Cancelled[/info]")
                return CopyResult(success=True, copied_count=0)

    def _parse_agent_file(self, agent_file: Path, agent_type: str) -> AgentInfo:
        """Parse agent file to extract information."""
        name = agent_file.name
        description = "AI Agent"
        specializations = []

        try:
            content = agent_file.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Extract description from first few lines or markdown headers
            for line in lines[:10]:
                line = line.strip()
                if line.startswith("#") and len(line) > 2:
                    description = line.lstrip("#").strip()
                    break
                elif line and not line.startswith("#") and len(line) > 10:
                    description = line[:100] + "..." if len(line) > 100 else line
                    break

            # Look for specializations or capabilities
            content_lower = content.lower()
            if "security" in content_lower:
                specializations.append("Security")
            if "code review" in content_lower or "review" in content_lower:
                specializations.append("Code Review")
            if "architecture" in content_lower:
                specializations.append("Architecture")
            if "ux" in content_lower or "user experience" in content_lower:
                specializations.append("UX/UI")
            if "refactor" in content_lower or "simplif" in content_lower:
                specializations.append("Refactoring")

        except Exception:
            # If we can't read the file, use defaults
            pass

        return AgentInfo(
            name=name,
            type=agent_type,
            path=agent_file,
            description=description,
            specializations=specializations,
        )

    def _files_identical(self, file1: Path, file2: Path) -> bool:
        """Check if two files have identical content."""
        try:
            import filecmp

            return filecmp.cmp(file1, file2, shallow=False)
        except Exception:
            return False
