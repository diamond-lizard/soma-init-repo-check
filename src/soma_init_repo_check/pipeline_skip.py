#!/usr/bin/env python3
"""Progress emission for locally-skipped repos in the pipeline."""
from __future__ import annotations

from typing import Any, Callable


def count_not_github(results: list[dict[str, Any]]) -> int:
    """Count skipped:not_github entries in the results list.

    Input: results -- list of result entry dicts.
    Output: number of not_github entries.
    """
    return sum(
        1 for r in results if r.get("status") == "skipped:not_github"
    )


def emit_skipped_progress(
    results: list[dict[str, Any]],
    total: int,
    quiet: bool,
    emit_fn: Callable[[int, int, str, str], None],
) -> int:
    """Emit skip-format progress messages for not_github repos.

    Iterates through results and emits a skip-format progress
    message for each skipped:not_github entry. When quiet is True,
    counts but does not emit messages.

    Input: results -- list with skipped entries.
           total -- total unique repo count for progress display.
           quiet -- suppress output if True.
           emit_fn -- callable to emit skip messages (emit_skipping).
    Output: counter value after processing all skip entries.
    """
    counter = 0
    if quiet:
        return count_not_github(results)
    for r in results:
        if r.get("status") != "skipped:not_github":
            continue
        counter += 1
        repo = r.get("repo", "unknown")
        emit_fn(counter, total, repo, "not on GitHub")
    return counter
