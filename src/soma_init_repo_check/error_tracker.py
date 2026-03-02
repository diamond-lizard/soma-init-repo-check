#!/usr/bin/env python3
"""Per-host error threshold tracking and abort logic."""
from __future__ import annotations

import json
import sys

from soma_init_repo_check.types import ErrorEntry
from soma_init_repo_check.types import ResultEntry


_MAX_ERRORS_PER_HOST = 5


class HostErrorTracker:
    """Track non-rate-limit error counts per host.

    Counts 4xx (non-rate-limit), 5xx failures, and network errors.
    A 5xx with successful retry counts as 0 errors. A 5xx with
    failed retry counts as 2 errors.
    """

    def __init__(self) -> None:
        """Initialize with empty error counts."""
        self._counts: dict[str, int] = {}

    def add_errors(self, host: str, count: int) -> None:
        """Add error count for a host.

        Input: host -- hostname string. count -- errors to add.
        Output: None. Mutates internal state.
        """
        self._counts[host] = self._counts.get(host, 0) + count

    def get_count(self, host: str) -> int:
        """Get current error count for a host.

        Input: host -- hostname string.
        Output: current error count integer.
        """
        return self._counts.get(host, 0)

    def check_threshold(self, host: str) -> bool:
        """Check if a host has exceeded the error threshold.

        Input: host -- hostname string.
        Output: True if threshold exceeded, False otherwise.
        """
        return self.get_count(host) >= _MAX_ERRORS_PER_HOST


def build_threshold_message(host: str, output_file: str) -> str:
    """Build the abort message for per-host error threshold.

    Input: host -- the offending hostname.
           output_file -- path or '-' for stdout.
    Output: descriptive abort message string.
    """
    count = _MAX_ERRORS_PER_HOST
    dest = "stdout" if output_file == "-" else output_file
    return (
        f"Aborted: per-host error threshold exceeded "
        f"({count} errors from {host}). "
        f"Partial results written to {dest}."
    )


def abort_threshold(
    host: str,
    output_file: str,
    partial_results: list[ResultEntry],
    errors: list[ErrorEntry],
    quiet: bool,
) -> None:
    """Abort the run after per-host error threshold exceeded.

    Writes partial results with interrupted=true, prints abort
    message to stderr, and exits with code 1.

    Input: host -- offending hostname. output_file -- path or '-'.
        partial_results -- results so far. errors -- errors so far.
        quiet -- suppress output if True.
    Output: never returns (calls sys.exit).
    """
    output: dict[str, list[ResultEntry] | list[ErrorEntry] | bool] = {
        "results": partial_results,
        "errors": errors,
        "interrupted": True,
    }
    json_str = json.dumps(output, indent=2)
    if output_file == "-":
        print(json_str)
    else:
        with open(output_file, "w", encoding="utf-8") as fh:
            fh.write(json_str)
            fh.write("\n")
    if not quiet:
        msg = build_threshold_message(host, output_file)
        print(msg, file=sys.stderr)
    sys.exit(1)
