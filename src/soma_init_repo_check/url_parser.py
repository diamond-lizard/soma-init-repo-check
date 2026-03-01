#!/usr/bin/env python3
"""Parse repository URLs and derive host identifiers."""
from __future__ import annotations

import sys
from urllib.parse import urlparse


def parse_repo_url(url: str) -> tuple[str, str, str, bool]:
    """Parse a repository URL into components.

    Determines if the URL points to github.com (case-insensitive).
    Extracts OWNER/REPO from the URL path, stripping any .git suffix.

    Input: full repository URL string.
    Output: (owner, repo, host_id, is_github) tuple.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    is_github = hostname.lower() == "github.com"
    path = parsed.path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    parts = path.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        msg = f"Error: cannot extract OWNER/REPO from URL: {url}"
        print(msg, file=sys.stderr)
        sys.exit(1)
    host_id = "github" if is_github else derive_host_id(hostname)
    return (parts[0], parts[1], host_id, is_github)


def derive_host_id(hostname: str) -> str:
    """Derive a short host identifier from a non-GitHub hostname.

    Removes the rightmost dot-separated segment (TLD). If the result
    is a single non-empty segment of at least 3 characters, uses it.
    Otherwise uses the full hostname.

    Input: hostname string (e.g., 'gitlab.com', 'sr.ht').
    Output: short host identifier string.
    """
    parts = hostname.rsplit(".", 1)
    if len(parts) == 2 and len(parts[0]) >= 3 and "." not in parts[0]:
        return parts[0]
    return hostname
