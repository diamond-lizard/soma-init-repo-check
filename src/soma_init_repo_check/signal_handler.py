#!/usr/bin/env python3
"""Keyboard interrupt handler for writing partial results."""
from __future__ import annotations

import errno
import json
import os
import sys
import tempfile
from typing import Any

from soma_init_repo_check.output_assembly import assemble_output
from soma_init_repo_check.summary import compute_summary
from soma_init_repo_check.summary import print_summary


def _write_atomic(output_file: str, content: str) -> str:
    """Write content atomically, returning actual destination path.

    Uses mkstemp + hard link. On EEXIST, keeps the temp file
    and returns its path after printing a warning to stderr.

    Input: output_file -- destination path.
           content -- JSON string to write.
    Output: path where results were actually written.
    """
    dir_name = os.path.dirname(os.path.abspath(output_file))
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix=".soma-tmp-")
    try:
        os.write(fd, content.encode("utf-8"))
        os.close(fd)
        fd = -1
        os.link(tmp_path, output_file)
        os.unlink(tmp_path)
        return output_file
    except OSError as exc:
        if fd >= 0:
            os.close(fd)
        if exc.errno == errno.EEXIST:
            msg = f"Warning: '{output_file}' created by another process."
            print(msg, file=sys.stderr)
            return tmp_path
        raise


def _write_data(output_file: str, data: dict[str, Any]) -> str:
    """Serialize data as JSON and write to output_file or stdout.

    Returns a description of where results were written.

    Input: output_file -- path or '-' for stdout.
           data -- dict to serialize as JSON.
    Output: destination string (file path or 'stdout').
    """
    content = json.dumps(data, indent=2) + "\n"
    if output_file == "-":
        sys.stdout.write(content)
        return "stdout"
    return _write_atomic(output_file, content)


def handle_interrupt(
    output_file: str,
    partial_results: list[dict[str, Any]],
    errors: list[dict[str, str]],
    init_count: int,
    quiet: bool,
) -> None:
    """Handle keyboard interrupt during the API processing loop.

    Writes partial results with interrupted=true, prints summary
    (unless --quiet), prints interrupt message, and exits with
    code 1. Only invoked when the API loop has begun.

    Input: output_file -- path or '-' for stdout.
           partial_results -- results collected before interrupt.
           errors -- errors collected before interrupt.
           init_count -- number of soma-init symbols for summary.
           quiet -- suppress summary if True.
    Output: never returns (calls sys.exit(1)).
    """
    data = assemble_output(partial_results, errors, interrupted=True)
    dest = _write_data(output_file, data)
    if not quiet:
        counters = compute_summary(init_count, partial_results, errors)
        print_summary(counters)
    print(f"Interrupted. Partial results written to {dest}.", file=sys.stderr)
    sys.exit(1)


def handle_pre_loop_interrupt() -> None:
    """Handle keyboard interrupt before the API loop begins.

    Prints 'Interrupted.' to stderr and exits with code 1
    without writing any output file.

    Output: never returns (calls sys.exit(1)).
    """
    print("Interrupted.", file=sys.stderr)
    sys.exit(1)
