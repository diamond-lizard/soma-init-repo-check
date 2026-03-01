#!/usr/bin/env python3
"""Abort logic when rate limit retries are exhausted."""
from __future__ import annotations

import json
import sys
from soma_init_repo_check.types import ErrorEntry, ResultEntry


class RateLimitExhausted(Exception):
    """Raised when rate limit retries are exhausted for a single request."""

    def __init__(self, message: str = "") -> None:
        """Store the abort message.

        Input: message -- descriptive abort reason.
        """
        super().__init__(message)
        self.message = message


def build_abort_message(output_file: str) -> str:
    """Build the abort message for rate limit exhaustion.

    Input: output_file -- path to the output file or '-' for stdout.
    Output: descriptive abort message string.
    """
    dest = "stdout" if output_file == "-" else output_file
    return (
        f"Aborted: rate limit retries exhausted. "
        f"Partial results written to {dest}."
    )


def abort_rate_limit(
    output_file: str,
    partial_results: list[ResultEntry],
    errors: list[ErrorEntry],
    quiet: bool,
) -> None:
    """Abort the run after rate limit retries exhausted.

    Writes partial results with interrupted=true to the output,
    prints abort message to stderr, and exits with code 1.

    Input: output_file -- path or '-' for stdout.
        partial_results -- results collected so far.
        errors -- errors collected so far.
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
        msg = build_abort_message(output_file)
        print(msg, file=sys.stderr)
    sys.exit(1)
