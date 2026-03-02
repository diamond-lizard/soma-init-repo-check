#!/usr/bin/env python3
"""Extract repo/host info from parsed soma init s-expressions."""
from __future__ import annotations

from typing import Any
from soma_init_repo_check.types import RepoInfo, ResultEntry
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
) -> tuple[list[RepoInfo], list[ResultEntry]]:
    """Extract repo declarations from a parsed soma init file.

    Input: parsed s-expression tree, init file name for results.
    Output: (repos, skipped) - repos has owner/repo/host/init_file keys.
    """
    repos: list[RepoInfo] = []
    skipped: list[ResultEntry] = []
    ensure_plists = _find_ensure_plists(tree)
    if not ensure_plists:
        skipped.append(_no_repo_entry(init_file))
        return repos, skipped
    found_any = False
    for plist in ensure_plists:
        found = _classify_plist(
            plist, init_file, repos, skipped,
        )
        if found:
            found_any = True
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
    plist: list[Any],
    init_file: str,
    repos: list[RepoInfo],
    skipped: list[ResultEntry],
) -> bool:
    """Classify a plist and append to repos or skipped.

    Input: plist from :ensure, init file name, target lists.
    Output: True if a :repo was found, False otherwise.
    """
    repo_val = _get_keyword_str(plist, ":repo")
    if repo_val is None:
        return False
    host_val = _get_keyword_sym(plist, ":host")
    if host_val is None:
        skipped.append(_no_host_entry(init_file, repo_val))
        return True
    if host_val == "github":
        repos.append(_github_entry(repo_val, init_file))
        return True
    skipped.append(_not_github_entry(repo_val, host_val, init_file))
    return True

