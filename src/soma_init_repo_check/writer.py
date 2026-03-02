#!/usr/bin/env python3
"""Atomic file writing with tempfile.mkstemp() + os.link()."""
from __future__ import annotations

import errno
import json
import os
import sys
import tempfile
from typing import Any


def _current_umask() -> int:
    """Return the current process umask without changing it.

    Output: integer umask value.
    """
    mask = os.umask(0)
    os.umask(mask)
    return mask


def _apply_umask_permissions(path: str) -> None:
    """Set file permissions based on the process umask.

    Input: path -- file to chmod.
    Output: None. Sets mode to 0o666 & ~umask.
    """
    mode = 0o666 & ~_current_umask()
    os.chmod(path, mode)


def _handle_eexist(tmp_path: str, output_file: str) -> None:
    """Handle EEXIST from os.link by reporting the temp file path.

    Keeps the temp file so the user can recover results.
    Prints an error to stderr and exits with code 1.

    Input: tmp_path -- path to the temp file with results.
           output_file -- the intended output path that already exists.
    Output: Never returns; calls sys.exit(1).
    """
    msg = (
        f"Error: '{output_file}' was created by another process. "
        f"Results saved to: {tmp_path}"
    )
    print(msg, file=sys.stderr)
    sys.exit(1)


def write_atomic(output_file: str, data: dict[str, Any]) -> None:
    """Write JSON data atomically using mkstemp + hard link.

    Creates a temp file in the same directory as output_file,
    writes JSON content, then hard-links to the final path.
    On success, removes the temp file and sets permissions.

    Input: output_file -- destination path.
           data -- dict to serialize as JSON.
    Output: None. Raises on EEXIST or other OS errors.
    """
    content = json.dumps(data, indent=2) + "\n"
    dir_name = os.path.dirname(os.path.abspath(output_file))
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix=".soma-tmp-")
    try:
        os.write(fd, content.encode("utf-8"))
        os.close(fd)
        fd = -1
        os.link(tmp_path, output_file)
        os.unlink(tmp_path)
        _apply_umask_permissions(output_file)
    except OSError as exc:
        if fd >= 0:
            os.close(fd)
        if exc.errno == errno.EEXIST:
            _handle_eexist(tmp_path, output_file)
        raise


def write_stdout(data: dict[str, Any]) -> None:
    """Write JSON data directly to stdout for OUTPUT_FILE='-'.

    Input: data -- dict to serialize as JSON.
    Output: None. Writes to sys.stdout.
    """
    content = json.dumps(data, indent=2) + "\n"
    sys.stdout.write(content)


def write_output(output_file: str, data: dict[str, Any]) -> None:
    """Write JSON to output_file or stdout when output_file is '-'.

    Input: output_file -- path or '-'. data -- dict to serialize.
    Output: None.
    """
    if output_file == "-":
        write_stdout(data)
    else:
        write_atomic(output_file, data)
