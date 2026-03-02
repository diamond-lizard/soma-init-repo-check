#!/usr/bin/env python3
"""Discover and parse soma init .el files with path traversal protection."""
from __future__ import annotations

from pathlib import Path

from soma_init_repo_check.types import InitFileErrorEntry


def resolve_init_paths(
    symbols: list[str], emacs_dir: str,
) -> tuple[list[tuple[str, Path]], list[InitFileErrorEntry]]:
    """Build and validate file paths for each soma-init symbol.

    Constructs file paths in <emacs_dir>/soma/inits/ for each symbol.
    Rejects paths that escape the inits directory after full resolution.

    Input: list of symbol names, emacs directory path.
    Output: (valid_paths, errors) where valid_paths is a list of
            (symbol, resolved_path) tuples and errors is a list of
            error dicts with 'init_file' and 'error' keys.
    """
    inits_dir = (Path(emacs_dir).expanduser() / "soma" / "inits").resolve()
    valid: list[tuple[str, Path]] = []
    errors: list[InitFileErrorEntry] = []
    for symbol in symbols:
        filename = f"{symbol}.el"
        candidate = inits_dir / filename
        resolved = _resolve_safe(candidate, inits_dir)
        if resolved is None:
            errors.append(_path_error(filename, inits_dir))
            continue
        valid.append((symbol, resolved))
    return valid, errors


def _resolve_safe(path: Path, base: Path) -> Path | None:
    """Resolve a path and verify it stays within the base directory.

    Input: candidate path, base directory (both should be resolved).
    Output: resolved path if safe, None if path escapes base.
    """
    try:
        resolved = path.resolve()
    except OSError:
        return None
    if not _is_within(resolved, base):
        return None
    return resolved


def _is_within(path: Path, base: Path) -> bool:
    """Check if a resolved path is within a base directory.

    Input: resolved path, resolved base directory.
    Output: True if path is within base.
    """
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def _path_error(filename: str, inits_dir: Path) -> InitFileErrorEntry:
    """Create an error dict for a path traversal violation.

    Input: filename that failed, inits directory path.
    Output: error dict with init_file and error keys.
    """
    return {
        "init_file": filename,
        "error": f"Path traversal: resolved path escapes {inits_dir}",
    }
