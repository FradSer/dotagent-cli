"""Security service implementation."""

import os
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from ...domain.exceptions import InvalidPathError, PathTraversalError, SecurityError
from ...interfaces.services import SecurityService


class SecurityServiceImpl(SecurityService):
    """Implementation of security service with comprehensive security checks."""

    def __init__(self, allowed_base_paths: Optional[list[Path]] = None) -> None:
        """Initialize security service.

        Args:
            allowed_base_paths: List of allowed base paths. Defaults to user home.
        """
        self._allowed_base_paths = allowed_base_paths or [Path.home()]

    def is_safe_path(self, path: Path, allowed_base: Optional[Path] = None) -> bool:
        """Check if a path is safe to access."""
        try:
            self.sanitize_path(str(path))
            return True
        except SecurityError:
            return False

    def sanitize_path(self, path: str) -> Path:
        """Sanitize a path for safe access."""
        if not path or not path.strip():
            raise InvalidPathError(path, "Path cannot be empty")

        # Resolve the path to handle . and .. components
        try:
            resolved_path = Path(path).resolve()
        except (OSError, ValueError) as e:
            raise InvalidPathError(path, f"Invalid path: {e}")

        # Check for path traversal attempts
        if ".." in Path(path).parts:
            # Allow .. only if the resolved path is still within allowed directories
            if not self._is_within_allowed_paths(resolved_path):
                raise PathTraversalError(path)

        # Check if the resolved path is within allowed base paths
        if not self._is_within_allowed_paths(resolved_path):
            raise PathTraversalError(path)

        # Check for suspicious patterns
        suspicious_patterns = [
            r"/proc/",
            r"/sys/",
            r"/dev/",
            r"/etc/passwd",
            r"/etc/shadow",
            r"\.ssh/",
            r"\.aws/",
            r"\.env",
        ]

        path_str = str(resolved_path)
        for pattern in suspicious_patterns:
            if re.search(pattern, path_str, re.IGNORECASE):
                raise InvalidPathError(
                    path, f"Access to sensitive path blocked: {pattern}"
                )

        return resolved_path

    def _is_within_allowed_paths(self, path: Path) -> bool:
        """Check if path is within allowed base paths."""
        try:
            for allowed_base in self._allowed_base_paths:
                resolved_base = allowed_base.resolve()
                if self._is_path_under_base(path, resolved_base):
                    return True
            return False
        except (OSError, ValueError):
            return False

    def _is_path_under_base(self, path: Path, base: Path) -> bool:
        """Check if path is under base directory."""
        try:
            path.relative_to(base)
            return True
        except ValueError:
            return False

    def is_safe_url(self, url: str) -> bool:
        """Check if a URL is safe to access."""
        if not url or not url.strip():
            return False

        try:
            parsed = urlparse(url)
        except Exception:
            return False

        # Allow only specific schemes
        allowed_schemes = {"http", "https", "git", "ssh"}
        if parsed.scheme.lower() not in allowed_schemes:
            return False

        # Block localhost and private IPs for HTTP/HTTPS
        if parsed.scheme.lower() in {"http", "https"}:
            hostname = parsed.hostname
            if hostname:
                # Block localhost
                if hostname.lower() in {"localhost", "127.0.0.1", "::1"}:
                    return False

                # Block private IP ranges (simplified check)
                if (
                    hostname.startswith("192.168.")
                    or hostname.startswith("10.")
                    or hostname.startswith("172.")
                ):
                    return False

        # Check for suspicious patterns
        suspicious_patterns = [
            r"javascript:",
            r"data:",
            r"file:",
            r"ftp:",
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False

        return True

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename for safe use."""
        if not filename or not filename.strip():
            raise InvalidPathError(filename, "Filename cannot be empty")

        # Remove or replace dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

        # Remove control characters
        sanitized = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", sanitized)

        # Handle reserved names on Windows
        reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }

        name_without_ext = sanitized.split(".")[0].upper()
        if name_without_ext in reserved_names:
            sanitized = f"_{sanitized}"

        # Ensure filename is not too long
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            max_name_len = 255 - len(ext)
            sanitized = name[:max_name_len] + ext

        # Ensure filename doesn't start/end with dots or spaces
        sanitized = sanitized.strip(". ")

        if not sanitized:
            raise InvalidPathError(
                filename, "Filename becomes empty after sanitization"
            )

        return sanitized

    def check_permissions(self, path: Path, operation: str) -> bool:
        """Check if we have permissions for an operation on a path."""
        try:
            if operation.lower() == "read":
                return os.access(path, os.R_OK)
            elif operation.lower() == "write":
                if path.exists():
                    return os.access(path, os.W_OK)
                else:
                    # Check parent directory write permission
                    return os.access(path.parent, os.W_OK)
            elif operation.lower() == "execute":
                return os.access(path, os.X_OK)
            else:
                return False
        except (OSError, ValueError):
            return False

    def mask_sensitive_data(self, data: str) -> str:
        """Mask sensitive data in strings (URLs, tokens, etc.)."""
        if not data:
            return data

        # Mask common sensitive patterns
        patterns = [
            # URLs with credentials
            (r"(https?://)[^:]+:[^@]+@", r"\1***:***@"),
            # SSH URLs
            (r"(git@[^:]+:)", r"\1***@"),
            # API tokens and keys
            (r"(token[=:])[^\s&]+", r"\1***", re.IGNORECASE),
            (r"(key[=:])[^\s&]+", r"\1***", re.IGNORECASE),
            (r"(password[=:])[^\s&]+", r"\1***", re.IGNORECASE),
            # AWS-style keys
            (r"(AKIA[0-9A-Z]{16})", r"AKIA***"),
            # Generic long base64-like strings (possible tokens)
            (r"([A-Za-z0-9+/]{40,})", lambda m: m.group(1)[:8] + "***"),
        ]

        masked = data
        for pattern, replacement, *flags in patterns:
            flag = flags[0] if flags else 0
            if callable(replacement):
                masked = re.sub(pattern, replacement, masked, flags=flag)
            else:
                masked = re.sub(pattern, replacement, masked, flags=flag)

        return masked
