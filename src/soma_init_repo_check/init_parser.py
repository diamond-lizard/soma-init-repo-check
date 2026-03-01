#!/usr/bin/env python3
"""Parse init.el to extract elpaca bootstrap repo and soma-inits list."""
from __future__ import annotations

from typing import Any
import sys
from pathlib import Path

import sexpdata

from soma_init_repo_check.elisp import strip_comments

_MAX_FILE_SIZE = 1_000_000


def read_init_el(emacs_dir: str) -> list[Any]:
    """Read and parse init.el from the given Emacs directory.

    Input: path to the Emacs directory (e.g., ~/.emacs.d/).
    Output: list of parsed s-expressions.
    """
    path = Path(emacs_dir).expanduser() / "init.el"
    if not path.exists():
        print(f"Error: init.el not found at {path}", file=sys.stderr)
        sys.exit(1)
    size = path.stat().st_size
    if size > _MAX_FILE_SIZE:
        msg = f"Error: init.el exceeds 1 MB ({size} bytes): {path}"
        print(msg, file=sys.stderr)
        sys.exit(1)
    content = path.read_text(encoding="utf-8", errors="replace")
    stripped = strip_comments(content)
    return _parse_sexp(stripped, path)


def _parse_sexp(content: str, path: Path) -> list[Any]:
    """Parse stripped Elisp content with sexpdata.

    Input: comment-stripped Elisp content, path for error messages.
    Output: list of parsed s-expressions.
    """
    try:
        return sexpdata.parse(content)
    except Exception as e:
        msg = f"Error: failed to parse {path}: {e}"
        print(msg, file=sys.stderr)
        sys.exit(1)


def extract_elpaca_repo_url(tree: list[Any]) -> str:
    """Find the :repo URL in elpaca-order from parsed init.el.

    Input: parsed s-expression tree from read_init_el.
    Output: repo URL string. Exits with error if not found.
    """
    for form in tree:
        if not isinstance(form, list) or len(form) < 3:
            continue
        if not _is_symbol(form[0], "defvar"):
            continue
        if not _is_symbol(form[1], "elpaca-order"):
            continue
        return _extract_repo_keyword(form[2])
    print("Error: elpaca-order not found in init.el", file=sys.stderr)
    sys.exit(1)


def _extract_repo_keyword(value: Any) -> str:
    """Extract :repo string from an elpaca-order plist value."""
    items = value[0] if isinstance(value, sexpdata.Quoted) else value
    for i, item in enumerate(items):
        if not _is_symbol(item, ":repo") or i + 1 >= len(items):
            continue
        if isinstance(items[i + 1], str):
            return str(items[i + 1])
    print("Error: :repo not found in elpaca-order", file=sys.stderr)
    sys.exit(1)


def extract_soma_inits(tree: list[Any]) -> list[str]:
    """Extract soma-inits symbol list from parsed init.el.

    Input: parsed s-expression tree from read_init_el.
    Output: list of symbol name strings. Exits if not found.
    """
    for form in tree:
        if not isinstance(form, list) or len(form) < 3:
            continue
        if not _is_symbol(form[0], "setq"):
            continue
        if not _is_symbol(form[1], "soma-inits"):
            continue
        items = form[2][0] if isinstance(form[2], sexpdata.Quoted) else form[2]
        return [s.value() for s in items if isinstance(s, sexpdata.Symbol)]
    print("Error: soma-inits not found in init.el", file=sys.stderr)
    sys.exit(1)

def _is_symbol(obj: Any, name: str) -> bool:
    """Check if obj is a sexpdata Symbol with the given name."""
    return isinstance(obj, sexpdata.Symbol) and obj.value() == name
