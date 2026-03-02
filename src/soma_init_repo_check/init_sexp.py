#!/usr/bin/env python3
"""S-expression helpers for init.el parsing."""
from __future__ import annotations

import sys

import sexpdata
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sexpdata import SexpNode



def is_symbol(obj: SexpNode, name: str) -> bool:
    """Check if obj is a sexpdata Symbol with the given name."""
    return isinstance(obj, sexpdata.Symbol) and obj.value() == name


def extract_repo_keyword(value: SexpNode) -> str:
    """Extract :repo string from an elpaca-order plist value.

    Unwraps Quoted values and searches for :repo keyword.

    Input: the plist value from the elpaca-order defvar.
    Output: the :repo URL string. Exits if not found.
    """
    items = value[0] if isinstance(value, sexpdata.Quoted) else value
    if not isinstance(items, list):
        print("Error: :repo not found in elpaca-order", file=sys.stderr)
        sys.exit(1)
    return _find_repo_str(items)


def _find_repo_str(items: list[SexpNode]) -> str:
    """Search a plist-like list for the :repo string value.

    Input: list of sexp nodes from an elpaca-order plist.
    Output: the :repo URL string. Exits if not found.
    """
    for i, item in enumerate(items):
        if not is_symbol(item, ":repo") or i + 1 >= len(items):
            continue
        if isinstance(items[i + 1], str):
            return str(items[i + 1])
    print("Error: :repo not found in elpaca-order", file=sys.stderr)
    sys.exit(1)
