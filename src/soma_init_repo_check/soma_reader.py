#!/usr/bin/env python3
"""Read and parse individual soma init .el files."""
from __future__ import annotations

from pathlib import Path

import sexpdata

from soma_init_repo_check.elisp import strip_comments

_MAX_FILE_SIZE = 1_000_000


def read_init_file(
    path: Path,
) -> tuple[list | None, dict[str, str] | None]:
    """Read and parse a single soma init .el file.

    Checks file existence and size, reads with utf-8/replace,
    strips comments, and parses with sexpdata.

    Input: resolved path to the .el file.
    Output: (parsed_tree, None) on success, or (None, error_dict)
            on failure. Error dict has 'init_file' and 'error' keys.
    """
    filename = path.name
    if not path.exists():
        return None, _file_error(filename, "File not found")
    size = path.stat().st_size
    if size > _MAX_FILE_SIZE:
        msg = f"File exceeds 1 MB ({size} bytes)"
        return None, _file_error(filename, msg)
    content = path.read_text(encoding="utf-8", errors="replace")
    stripped = strip_comments(content)
    return _try_parse(stripped, filename)


def _try_parse(
    content: str, filename: str,
) -> tuple[list | None, dict[str, str] | None]:
    """Attempt to parse stripped Elisp content.

    Input: comment-stripped content, filename for error messages.
    Output: (parsed_tree, None) or (None, error_dict).
    """
    try:
        tree = sexpdata.parse(content)
        return tree, None
    except Exception as e:
        return None, _file_error(filename, f"Parse error: {e}")


def _file_error(filename: str, msg: str) -> dict[str, str]:
    """Create an error dict for a file-level problem.

    Input: init file name, error message.
    Output: dict with init_file and error keys.
    """
    return {"init_file": filename, "error": msg}
