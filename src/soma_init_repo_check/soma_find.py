#!/usr/bin/env python3
"""Find use-package :ensure plists in parsed soma init s-expressions."""
from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sexpdata import SexpNode

from soma_init_repo_check.soma_entries import _is_sym


def find_ensure_plists(tree: list[SexpNode]) -> list[list[SexpNode]]:
    """Find all :ensure plist values in use-package forms.

    Input: parsed s-expression tree.
    Output: list of plist lists from :ensure directives.
    """
    plists: list[list[SexpNode]] = []
    for form in tree:
        if not isinstance(form, list) or len(form) < 2:
            continue
        if not _is_sym(form[0], "use-package"):
            continue
        plist = _get_ensure_value(form)
        if plist is not None:
            plists.append(plist)
    return plists


def _get_ensure_value(form: list[SexpNode]) -> list[SexpNode] | None:
    """Extract the :ensure plist from a use-package form.

    Input: a use-package s-expression list.
    Output: the plist following :ensure, or None.
    """
    for i, item in enumerate(form):
        if not _is_sym(item, ":ensure") or i + 1 >= len(form):
            continue
        val = form[i + 1]
        if isinstance(val, list):
            return val
    return None
