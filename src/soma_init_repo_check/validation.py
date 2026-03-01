#!/usr/bin/env python3
"""Validate OWNER/REPO strings against GitHub naming conventions."""
from __future__ import annotations

import re


_COMPONENT_PATTERN = re.compile(r"^[A-Za-z0-9\-._]+$")


def validate_owner_repo(owner_repo: str) -> str | None:
    """Validate an OWNER/REPO string for GitHub naming conventions.

    Splits on '/' and checks each component individually: only
    alphanumeric characters, hyphens, dots, and underscores are
    allowed. No path separators, whitespace, or control characters.

    Input: owner_repo -- string in "OWNER/REPO" format.
    Output: None if valid, descriptive error string if invalid.
    """
    parts = owner_repo.split("/")
    if len(parts) != 2:
        return f"Invalid OWNER/REPO '{owner_repo}': expected exactly one '/'"
    owner, repo = parts
    if not owner:
        return f"Invalid OWNER/REPO '{owner_repo}': owner is empty"
    if not repo:
        return f"Invalid OWNER/REPO '{owner_repo}': repo is empty"
    if not _COMPONENT_PATTERN.match(owner):
        return f"Invalid owner '{owner}': only alphanumeric, hyphens, dots, underscores allowed"
    if not _COMPONENT_PATTERN.match(repo):
        return f"Invalid repo '{repo}': only alphanumeric, hyphens, dots, underscores allowed"
    return None
