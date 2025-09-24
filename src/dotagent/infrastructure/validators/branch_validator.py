"""Git branch name validation specialist."""

from ...domain.constants import ValidationLimits
from ...domain.exceptions import SyncValidationError


class BranchNameValidator:
    """Specialized validator for Git branch names."""

    _INVALID_CHARS = [" ", "~", "^", ":", "?", "*", "[", "\\", "\x7f"]
    _RESERVED_NAMES = ["HEAD", "@"]

    def validate(self, branch: str) -> str:
        """Validate a Git branch name."""
        if not branch or not branch.strip():
            raise SyncValidationError(["Branch name cannot be empty"])

        branch = branch.strip()
        validation_errors = []

        # Check length
        if len(branch) > ValidationLimits.MAX_BRANCH_NAME_LENGTH:
            validation_errors.append(
                f"Branch name too long (max {ValidationLimits.MAX_BRANCH_NAME_LENGTH} characters)"
            )

        # Check for invalid characters
        found_invalid = [char for char in self._INVALID_CHARS if char in branch]
        if found_invalid:
            validation_errors.append(
                f"Branch name contains invalid characters: {found_invalid}"
            )

        # Check for invalid patterns
        if branch.startswith(".") or branch.endswith("."):
            validation_errors.append("Branch name cannot start or end with a dot")

        if branch.startswith("/") or branch.endswith("/"):
            validation_errors.append("Branch name cannot start or end with a slash")

        if "//" in branch:
            validation_errors.append("Branch name cannot contain consecutive slashes")

        if branch.endswith(".lock"):
            validation_errors.append("Branch name cannot end with .lock")

        # Check for control characters
        if any(ord(char) < 32 for char in branch):
            validation_errors.append("Branch name cannot contain control characters")

        # Reserved names
        if branch in self._RESERVED_NAMES:
            validation_errors.append(f"'{branch}' is a reserved branch name")

        if validation_errors:
            raise SyncValidationError(validation_errors)

        return branch
