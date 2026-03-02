#!/usr/bin/env python3
"""Deduplicate repos by (host, OWNER/REPO) tuple."""
from __future__ import annotations

from soma_init_repo_check.types import RepoInfo


def deduplicate_repos(
    repos: list[RepoInfo],
) -> list[RepoInfo]:
    """Remove duplicate repos, keeping the alphabetically first init file.

    Deduplication key is (host, OWNER/REPO). The same OWNER/REPO on
    different hosts is treated as distinct. Config-level statuses
    (skipped:no_repo_directive, skipped:no_host) are not handled here;
    they are passed through separately.

    Input: list of repo dicts with owner, repo, host, init_file keys.
    Output: deduplicated list of repo dicts.
    """
    seen: dict[tuple[str, str], RepoInfo] = {}
    for entry in repos:
        key = _dedup_key(entry)
        if key not in seen or entry["init_file"] < seen[key]["init_file"]:
            seen[key] = entry
    return list(seen.values())


def _dedup_key(entry: RepoInfo) -> tuple[str, str]:
    """Compute the deduplication key for a repo entry.

    Input: repo dict with owner, repo, host keys.
    Output: (host, "OWNER/REPO") tuple.
    """
    owner_repo = f"{entry['owner']}/{entry['repo']}"
    return (entry["host"], owner_repo)
