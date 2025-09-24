"""Interactive service interface for dependency inversion."""

from abc import ABC, abstractmethod
from pathlib import Path


class InteractiveServiceInterface(ABC):
    """Interface defining interactive operations for dependency inversion."""

    @abstractmethod
    def select_sync_items(
        self,
        working_dir: Path,
        force: bool = False,
        operation_type: str = "bidirectional",
    ) -> list[tuple[str, str]]:
        """Prompt user to select which sync items to process.

        Args:
            working_dir: The cloned repository working directory
            force: If True, skip interactive selection and return all items
            operation_type: Type of operation ("pull", "push", "bidirectional")

        Returns:
            List of selected (item_name, item_type) tuples
        """
        ...
