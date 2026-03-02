#!/usr/bin/env python3
"""Early existence check for output file before expensive work."""
from __future__ import annotations

import os
import sys


def check_output_exists(output_file: str) -> None:
    """Exit with error if output_file already exists on disk.

    Skipped when output_file is '-' (stdout mode).
    This runs before any expensive work (token retrieval,
    parsing, API calls) to fail fast.

    Input: output_file -- path to check, or '-' for stdout.
    Output: None. Calls sys.exit(1) if file exists.
    """
    if output_file == "-":
        return
    if os.path.exists(output_file):
        msg = (
            f"Error: '{output_file}' already exists. "
            "It may be from a previous interrupted run. "
            "Delete it or use a different path."
        )
        print(msg, file=sys.stderr)
        sys.exit(1)
