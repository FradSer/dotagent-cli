"""Service for handling local-agents file selection and processing."""

from pathlib import Path

from rich.console import Console


class LocalAgentsService:
    """Service for interactive local-agents file management."""

    def __init__(self):
        self.console = Console()

    def select_agent_files(
        self, local_agents_path: Path, force: bool = False
    ) -> list[Path]:
        """
        Prompt user to select which agent files to sync.

        Args:
            local_agents_path: Path to the local-agents directory
            force: If True, skip interactive selection and return all .md files

        Returns:
            List of selected agent file paths
        """
        if not local_agents_path.exists():
            self.console.print("[yellow]No local-agents directory found[/yellow]")
            return []

        # Find all .md files in local-agents
        md_files = list(local_agents_path.glob("*.md"))

        if not md_files:
            self.console.print("[yellow]No .md files found in local-agents[/yellow]")
            return []

        if force:
            return md_files

        # Create choices for the prompt
        choices = []
        choice_to_path = {}

        for md_file in md_files:
            choice_text = f"{md_file.name}"
            choices.append(choice_text)
            choice_to_path[choice_text] = md_file

        if not choices:
            return []

        # Show interactive selection using simple prompts
        self.console.print("\n[bold blue]Select agent files to sync:[/bold blue]")
        self.console.print("[dim]Enter file numbers separated by spaces (e.g. '1 3 5') or 'all' for all files[/dim]")

        # Display numbered choices
        for i, choice in enumerate(choices, 1):
            self.console.print(f"  [cyan]{i}.[/cyan] {choice}")

        try:
            user_input = input("\nEnter your selection: ").strip()

            if not user_input:
                self.console.print("[yellow]No agent files selected[/yellow]")
                return []

            if user_input.lower() == 'all':
                selected_choice_texts = choices
            else:
                # Parse space-separated numbers
                try:
                    indices = [int(x) for x in user_input.split()]
                    selected_choice_texts = [choices[i-1] for i in indices if 1 <= i <= len(choices)]
                except (ValueError, IndexError):
                    self.console.print("[red]Invalid selection. Please enter valid numbers.[/red]")
                    return []

            if not selected_choice_texts:
                self.console.print("[yellow]No agent files selected[/yellow]")
                return []

            # Convert selected choice texts back to file paths
            selected_files = [
                choice_to_path[choice] for choice in selected_choice_texts
            ]
            return selected_files

        except (KeyboardInterrupt, EOFError):
            self.console.print("\n[yellow]Agent file selection cancelled[/yellow]")
            return []

    def copy_selected_files(
        self, source_dir: Path, target_dir: Path, selected_files: list[Path]
    ) -> int:
        """
        Copy selected agent files from source to target directory.

        Args:
            source_dir: Source directory (remote local-agents)
            target_dir: Target directory (local .claude/agents)
            selected_files: List of files to copy (relative to source_dir)

        Returns:
            Number of files successfully copied
        """
        if not selected_files:
            return 0

        # Ensure target directory exists
        target_dir.mkdir(parents=True, exist_ok=True)

        copied_count = 0
        for file_path in selected_files:
            try:
                # Get relative path from source_dir
                relative_path = file_path.relative_to(source_dir)
                target_file = target_dir / relative_path

                # Copy file content
                target_file.write_text(file_path.read_text(), encoding="utf-8")
                copied_count += 1
                self.console.print(f"[green]Copied: {relative_path}[/green]")

            except Exception as e:
                self.console.print(f"[red]Failed to copy {file_path.name}: {e}[/red]")

        return copied_count
