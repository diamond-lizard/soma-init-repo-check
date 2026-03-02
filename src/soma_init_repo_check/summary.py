#!/usr/bin/env python3
"""Compute and print the multi-line summary to stderr."""
from __future__ import annotations

import sys
from typing import Any

from soma_init_repo_check.summary_counts import count_errors
from soma_init_repo_check.summary_counts import count_results


def compute_summary(
    init_count: int,
    results: list[dict[str, Any]],
    errors: list[dict[str, str]],
) -> dict[str, int]:
    """Compute all summary counters from results and errors.

    Input: init_count -- number of soma-init symbols.
           results -- list of result entry dicts.
           errors -- list of error entry dicts.
    Output: dict of counter names to integer values.
    """
    rc = count_results(results)
    ec = count_errors(errors)
    checked = rc["forks"] + rc["not_a_fork"] + ec["api_errors"]
    unique = checked + rc["not_github"] + ec["validation"]
    return {
        "init_count": init_count,
        "no_repo": rc["no_repo"],
        "no_host": rc["no_host"],
        "init_errors": ec["init_errors"],
        "unique": unique,
        "checked": checked,
        "forks": rc["forks"],
        "behind": rc["behind"],
        "skipped": rc["not_github"],
        "validation_errors": ec["validation"],
        "errors": ec["api_errors"],
    }


def print_summary(counters: dict[str, int]) -> None:
    """Print the multi-line summary to stderr.

    Input: counters -- dict from compute_summary.
    Output: None. Prints to stderr.
    """
    labels = [
        ("Entries in soma-inits", "init_count"),
        ("Init files with no repo", "no_repo"),
        ("Init files with no host", "no_host"),
        ("Init file errors", "init_errors"),
        ("Unique repos", "unique"),
        ("Repos checked", "checked"),
        ("Forks", "forks"),
        ("Behind upstream", "behind"),
        ("Skipped", "skipped"),
        ("Validation errors", "validation_errors"),
        ("Errors", "errors"),
    ]
    for label, key in labels:
        print(f"{label}: {counters[key]}", file=sys.stderr)
