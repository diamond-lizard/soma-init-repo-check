#!/usr/bin/env python3
"""Count result and error entries by category for the summary."""
from __future__ import annotations

from typing import Any


def count_results(results: list[dict[str, Any]]) -> dict[str, int]:
    """Count result entries by status category.

    Input: results -- list of result entry dicts.
    Output: dict with no_repo, no_host, not_github, forks, behind,
            not_a_fork counts.
    """
    counts: dict[str, int] = {
        "no_repo": 0, "not_github": 0, "forks": 0,
        "behind": 0, "not_a_fork": 0,
    }
    host_files: set[str] = set()
    for r in results:
        status = r.get("status", "")
        if status == "skipped:no_repo_directive":
            counts["no_repo"] += 1
        elif status == "skipped:no_host":
            host_files.add(r["init_file"])
        elif status == "skipped:not_github":
            counts["not_github"] += 1
        elif status == "fork":
            counts["forks"] += 1
            if r.get("behind_by", 0) > 0:
                counts["behind"] += 1
        elif status == "skipped:not_a_fork":
            counts["not_a_fork"] += 1
    counts["no_host"] = len(host_files)
    return counts


def count_errors(errors: list[dict[str, str]]) -> dict[str, int]:
    """Count error entries by category.

    Init file errors have 'init_file' but no 'repo_url'. Validation
    errors have 'repo' but no 'repo_url' or 'init_file'. API errors
    have 'repo_url'.

    Input: errors -- list of error entry dicts.
    Output: dict with init_errors, validation, api_errors counts.
    """
    init_errs = validation = api_errs = 0
    for e in errors:
        if "init_file" in e and "repo_url" not in e:
            init_errs += 1
        elif "repo" in e and "repo_url" not in e:
            validation += 1
        elif "repo_url" in e:
            api_errs += 1
    return {
        "init_errors": init_errs,
        "validation": validation,
        "api_errors": api_errs,
    }
