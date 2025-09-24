"""Interactive service for user prompts and selections."""

from typing import List, Tuple
from pathlib import Path

import inquirer
from rich.console import Console

from dotagent.domain.constants import SyncItems


class InteractiveSyncService:
    """Service for interactive sync item selection."""

    def __init__(self):
        self.console = Console()

    def select_sync_items(
        self,
        working_dir: Path,
        force: bool = False,
        operation_type: str = "bidirectional",
    ) -> List[Tuple[str, str]]:
        """
        Prompt user to select which sync items to process.

        Args:
            working_dir: The cloned repository working directory
            force: If True, skip interactive selection and return all items
            operation_type: Type of operation ("pull", "push", "bidirectional")

        Returns:
            List of selected (item_name, item_type) tuples
        """
        if force:
            return self._get_all_available_items(working_dir, operation_type)

        available_items = self._get_all_available_items(working_dir, operation_type)

        if not available_items:
            self.console.print("[yellow]No sync items found in repository[/yellow]")
            return []

        # Separate global and local items
        global_items = []
        local_items = []

        for item_name, item_type in available_items:
            if item_name == "local-agents":
                local_items.append((item_name, item_type))
            else:
                global_items.append((item_name, item_type))

        # Create choices and mappings
        choices = []
        choice_to_item = {}
        default_choices = []

        # Add global items (pre-selected)
        for item_name, item_type in global_items:
            description = self._get_item_description(item_name)
            choice_text = f"{item_name} ({description})"
            choices.append(choice_text)
            choice_to_item[choice_text] = (item_name, item_type)
            default_choices.append(choice_text)  # Global items are pre-selected

        # Add local items (not pre-selected)
        for item_name, item_type in local_items:
            description = self._get_item_description(item_name)
            choice_text = f"{item_name} ({description})"
            choices.append(choice_text)
            choice_to_item[choice_text] = (item_name, item_type)

        if not choices:
            return []

        # Show interactive selection
        self.console.print("\n[bold blue]Select items to sync:[/bold blue]")
        self.console.print("[dim]Use space to select/deselect, enter to confirm[/dim]")

        questions = [
            inquirer.Checkbox(
                "selected_items",
                message="Select sync items",
                choices=choices,
                default=default_choices,
            )
        ]

        try:
            answers = inquirer.prompt(questions)
            if answers is None:  # User cancelled
                self.console.print("[yellow]Sync cancelled by user[/yellow]")
                return []

            selected_choice_texts = answers.get("selected_items", [])

            if not selected_choice_texts:
                self.console.print("[yellow]No items selected for sync[/yellow]")
                return []

            # Convert selected choice texts back to (item_name, item_type) tuples
            selected_items = [
                choice_to_item[choice] for choice in selected_choice_texts
            ]

            # Debug output
            self.console.print(f"[dim]Selected choices: {selected_choice_texts}[/dim]")
            self.console.print(f"[dim]Selected items: {selected_items}[/dim]")

            return selected_items

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Sync cancelled by user[/yellow]")
            return []

    def _get_all_available_items(
        self, working_dir: Path, operation_type: str = "bidirectional"
    ) -> List[Tuple[str, str]]:
        """Get all available sync items based on operation type."""
        from pathlib import Path

        available_items = []
        claude_dir = Path.home() / ".claude"

        if operation_type == "push":
            # For push operations, check local items
            for item_name, item_type in SyncItems.GLOBAL_ITEMS:
                local_path = claude_dir / item_name
                if local_path.exists():
                    available_items.append((item_name, item_type))

            # Note: local-agents is not relevant for push operations
            # since it goes from remote to local, not the other way around
        else:
            # For pull and bidirectional operations, check remote items
            for item_name, item_type in SyncItems.GLOBAL_ITEMS:
                remote_path = working_dir / item_name
                if remote_path.exists():
                    available_items.append((item_name, item_type))

            # Check local items (local-agents)
            for item_tuple in SyncItems.LOCAL_ITEMS:
                item_name = item_tuple[0]  # "local-agents"
                item_type = item_tuple[1]  # "dir"
                remote_path = working_dir / item_name
                if remote_path.exists():
                    available_items.append((item_name, item_type))

        return available_items

    def _get_item_description(self, item_name: str) -> str:
        """Get description for sync item."""
        descriptions = {
            "agents": "Global AI agents",
            "commands": "Global commands",
            "CLAUDE.md": "Global configuration file",
            "local-agents": "Project-specific agents",
        }
        return descriptions.get(item_name, "Configuration item")
