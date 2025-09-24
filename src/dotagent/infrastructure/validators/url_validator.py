"""URL validation specialist."""

import re
from urllib.parse import urlparse

from ...domain.exceptions import SyncValidationError


class URLValidator:
    """Specialized validator for repository URLs."""

    _GIT_URL_PATTERNS = [
        r"^https://github\.com/[^/]+/[^/]+(?:\.git)?/?$",
        r"^https://gitlab\.com/[^/]+/[^/]+(?:\.git)?/?$",
        r"^https://bitbucket\.org/[^/]+/[^/]+(?:\.git)?/?$",
        r"^git@github\.com:[^/]+/[^/]+\.git$",
        r"^git@gitlab\.com:[^/]+/[^/]+\.git$",
        r"^ssh://git@[^/]+/[^/]+/[^/]+\.git$",
    ]

    def validate(self, url: str) -> str:
        """Validate a repository URL."""
        if not url or not url.strip():
            raise SyncValidationError(["URL cannot be empty"])

        url = url.strip()

        # Basic safety check
        if not self._is_safe_url(url):
            raise SyncValidationError([f"Unsafe or invalid URL: {url}"])

        try:
            parsed = urlparse(url)
        except Exception:
            raise SyncValidationError([f"Invalid URL format: {url}"])

        # Validate specific URL patterns for Git repositories
        if not self._is_valid_git_url(url):
            # Allow other HTTPS URLs but warn
            if parsed.scheme in ["https", "http"]:
                return url
            else:
                raise SyncValidationError([f"Unsupported repository URL format: {url}"])

        return url

    def _is_safe_url(self, url: str) -> bool:
        """Check if URL is safe for access."""
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
                if hostname.lower() in {"localhost", "127.0.0.1", "::1"}:
                    return False
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

    def _is_valid_git_url(self, url: str) -> bool:
        """Check if URL matches valid Git repository patterns."""
        return any(
            re.match(pattern, url, re.IGNORECASE) for pattern in self._GIT_URL_PATTERNS
        )
