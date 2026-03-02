#!/usr/bin/env python3
"""Parse init.el to extract elpaca bootstrap repo and soma-inits list."""
from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sexpdata import SexpNode

import sys
from pathlib import Path

import sexpdata

from soma_init_repo_check.elisp import strip_comments
from soma_init_repo_check.init_sexp import extract_repo_keyword, is_symbol

_MAX_FILE_SIZE = 1_000_000


def read_init_el(emacs_dir: str) -> list[SexpNode]:
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


def _parse_sexp(content: str, path: Path) -> list[SexpNode]:
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


def extract_elpaca_repo_url(tree: list[SexpNode]) -> str:
    """Find the :repo URL in elpaca-order from parsed init.el.

    Input: parsed s-expression tree from read_init_el.
    Output: repo URL string. Exits with error if not found.
    """
    for form in tree:
        if not isinstance(form, list) or len(form) < 3:
            continue
        if not is_symbol(form[0], "defvar"):
            continue
        if not is_symbol(form[1], "elpaca-order"):
            continue
        return extract_repo_keyword(form[2])
    print("Error: elpaca-order not found in init.el", file=sys.stderr)
    sys.exit(1)

def extract_soma_inits(tree: list[SexpNode]) -> list[str]:
    """Extract soma-inits symbol list from parsed init.el.

    Input: parsed s-expression tree from read_init_el.
    Output: list of symbol name strings. Exits if not found.
    """
    for form in tree:
        if not isinstance(form, list) or len(form) < 3:
            continue
        if not is_symbol(form[0], "setq"):
            continue
        if not is_symbol(form[1], "soma-inits"):
            continue
        val = form[2]
        items = val[0] if isinstance(val, sexpdata.Quoted) else val
        if not isinstance(items, list):
            continue
        return [s.value() for s in items if isinstance(s, sexpdata.Symbol)]
    print("Error: soma-inits not found in init.el", file=sys.stderr)
    sys.exit(1)

