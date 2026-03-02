#!/usr/bin/env python3
"""Progress messages and summary output for repo processing."""
from __future__ import annotations

import sys


def emit_checking(index: int, total: int, owner_repo: str) -> None:
    """Print a progress message for a repo being checked via API.

    Input: index -- 1-based counter. total -- total unique repos.
           owner_repo -- OWNER/REPO string.
    Output: None. Prints to stderr.
    """
    print(f"Checking repo {index}/{total}: {owner_repo}...", file=sys.stderr)


def emit_skipping(
    index: int, total: int, owner_repo: str, reason: str,
) -> None:
    """Print a progress message for a locally skipped repo.

    Input: index -- 1-based counter. total -- total unique repos.
           owner_repo -- OWNER/REPO string. reason -- skip reason.
    Output: None. Prints to stderr.
    """
    print(
        f"Skipping repo {index}/{total}: {owner_repo} ({reason})...",
        file=sys.stderr,
    )

