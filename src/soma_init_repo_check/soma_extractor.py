#!/usr/bin/env python3
"""Extract repo/host info from parsed soma init s-expressions."""
from __future__ import annotations

from typing import Any
from soma_init_repo_check.soma_entries import (
    _get_keyword_str,
    _get_keyword_sym,
    _github_entry,
    _is_sym,
    _no_host_entry,
    _no_repo_entry,
    _not_github_entry,
)


def extract_repos(
    tree: list[Any], init_file: str,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Extract repo declarations from a parsed soma init file.

    Input: parsed s-expression tree, init file name for results.
    Output: (repos, skipped) - repos has owner/repo/host/init_file keys.
    """
    repos: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    ensure_plists = _find_ensure_plists(tree)
    if not ensure_plists:
        skipped.append(_no_repo_entry(init_file))
        return repos, skipped
    found_any = False
    for plist in ensure_plists:
        result = _classify_plist(plist, init_file)
        if result is None:
            continue
        found_any = True
        kind, entry = result
        if kind == "repo":
            repos.append(entry)
        else:
            skipped.append(entry)
    if not found_any:
        skipped.append(_no_repo_entry(init_file))
    return repos, skipped


def _find_ensure_plists(tree: list[Any]) -> list[list[Any]]:
    """Find all :ensure plist values in use-package forms.

    Input: parsed s-expression tree.
    Output: list of plist lists from :ensure directives.
    """
    plists: list[list[Any]] = []
    for form in tree:
        if not isinstance(form, list) or len(form) < 2:
            continue
        if not _is_sym(form[0], "use-package"):
            continue
        plist = _get_ensure_value(form)
        if plist is not None:
            plists.append(plist)
    return plists


def _get_ensure_value(form: list[Any]) -> list[Any] | None:
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


def _classify_plist(
    plist: list[Any], init_file: str,
) -> tuple[str, dict[str, str]] | None:
    """Classify an :ensure plist by host and repo presence.

    Input: plist from :ensure directive, init file name.
    Output: ('repo', entry) or ('skipped', entry) or None.
    """
    repo_val = _get_keyword_str(plist, ":repo")
    if repo_val is None:
        return None
    host_val = _get_keyword_sym(plist, ":host")
    if host_val is None:
        return ("skipped", _no_host_entry(init_file, repo_val))
    if host_val == "github":
        return ("repo", _github_entry(repo_val, init_file))
    return ("skipped", _not_github_entry(repo_val, host_val, init_file))

