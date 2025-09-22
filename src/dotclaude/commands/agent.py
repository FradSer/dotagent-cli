"""Agent management commands."""

import builtins
from typing import Optional

import typer
from rich.table import Table

from dotclaude.core.agent_manager import AgentManager
from dotclaude.utils.console import create_console

console = create_console()

app = typer.Typer(
    name="agent",
    help="Manage AI agents",
    rich_markup_mode="rich",
)


@app.command()
def list(
    local: bool = typer.Option(False, "--local", help="Show only local agents"),
    global_only: bool = typer.Option(False, "--global", help="Show only global agents"),
) -> None:
    """List available agents."""
    manager = AgentManager()

    if global_only:
        agents = manager.list_global_agents()
        title = "Global Agents"
    elif local:
        agents = manager.list_local_agents()
        title = "Local Agents"
    else:
        agents = manager.list_all_agents()
        title = "All Agents"

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Type", style="green")
    table.add_column("Description", style="white")

    for agent in agents:
        table.add_row(agent.name, agent.type, agent.description)

    console.print(table)


@app.command()
def copy(
    names: Optional[builtins.list[str]] = typer.Argument(
        None, help="Agent names to copy"
    ),
    all_agents: bool = typer.Option(False, "--all", help="Copy all local agents"),
    select: bool = typer.Option(False, "--select", help="Interactive selection"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing agents"),
) -> None:
    """Copy agents to current project."""
    manager = AgentManager()

    if all_agents:
        console.print("[bold blue]Copying all local agents...[/bold blue]")
        result = manager.copy_all_local_agents(force=force)
    elif select:
        console.print("[bold blue]Interactive agent selection...[/bold blue]")
        result = manager.copy_agents_interactive(force=force)
    elif names:
        console.print(f"[bold blue]Copying agents: {', '.join(names)}[/bold blue]")
        result = manager.copy_agents(names, force=force)
    else:
        console.print("Please specify agents to copy or use --all/--select")
        raise typer.Exit(1)

    if result.success:
        console.print(f"Copied {result.copied_count} agent(s)")
        if result.skipped_count > 0:
            console.print(f"Skipped {result.skipped_count} existing agent(s)")
    else:
        console.print(f"Copy failed: {result.error}")
        raise typer.Exit(1)


@app.command()
def info(
    name: str = typer.Argument(..., help="Agent name to show info for"),
) -> None:
    """Show detailed information about an agent."""
    manager = AgentManager()
    agent = manager.get_agent_info(name)

    if not agent:
        console.print(f"Agent '{name}' not found")
        raise typer.Exit(1)

    console.print(f"[bold cyan]{agent.name}[/bold cyan]")
    console.print(f"Type: [green]{agent.type}[/green]")
    console.print(f"Path: [yellow]{agent.path}[/yellow]")
    console.print(f"Description: {agent.description}")

    if agent.specializations:
        console.print("\n[bold]Specializations:[/bold]")
        for spec in agent.specializations:
            console.print(f"  • {spec}")


if __name__ == "__main__":
    app()
