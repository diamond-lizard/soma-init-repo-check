#!/usr/bin/env python3
"""Local work helpers: collect repos from init files."""
from __future__ import annotations

from typing import Any

from soma_init_repo_check.soma_extractor import extract_repos
from soma_init_repo_check.soma_parser import resolve_init_paths
from soma_init_repo_check.soma_reader import read_init_file


def collect_all_repos(
    soma_inits: list[str],
    emacs_dir: str,
    elpaca_owner: str,
    elpaca_repo: str,
    elpaca_host: str,
    elpaca_is_github: bool,
) -> tuple[list[dict[str, str]], list[dict[str, Any]], list[dict[str, str]]]:
    """Collect repos from all soma init files plus elpaca bootstrap.

    Input: soma_inits -- symbol names. emacs_dir -- Emacs dir path.
           elpaca_* -- parsed elpaca bootstrap repo info.
    Output: (github_repos, skipped_entries, error_entries).
    """
    repos: list[dict[str, str]] = []
    skipped: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    _add_elpaca(
        repos, skipped, elpaca_owner, elpaca_repo,
        elpaca_host, elpaca_is_github,
    )
    _add_soma_repos(repos, skipped, errors, soma_inits, emacs_dir)
    return repos, skipped, errors


def _add_elpaca(
    repos: list[dict[str, str]],
    skipped: list[dict[str, Any]],
    owner: str, repo: str, host: str, is_github: bool,
) -> None:
    """Add the elpaca bootstrap repo to repos or skipped list.

    Input: repos, skipped -- target lists. owner, repo, host,
           is_github -- parsed elpaca URL components.
    Output: None. Appends to repos or skipped.
    """
    if is_github:
        repos.append({
            "owner": owner, "repo": repo,
            "host": "github", "init_file": "init.el",
        })
        return
    skipped.append({
        "status": "skipped:not_github",
        "repo": f"{owner}/{repo}", "host": host,
        "init_file": "init.el",
    })


def _add_soma_repos(
    repos: list[dict[str, str]],
    skipped: list[dict[str, Any]],
    errors: list[dict[str, str]],
    soma_inits: list[str],
    emacs_dir: str,
) -> None:
    """Process all soma init files and collect repos.

    Input: repos, skipped, errors -- target lists.
           soma_inits -- symbol names. emacs_dir -- Emacs dir path.
    Output: None. Appends to repos, skipped, errors.
    """
    valid_paths, path_errors = resolve_init_paths(soma_inits, emacs_dir)
    errors.extend(path_errors)
    for symbol, path in valid_paths:
        tree, err = read_init_file(path)
        if err:
            errors.append(err)
            continue
        if tree is None:
            continue
        file_repos, file_skipped = extract_repos(tree, f"{symbol}.el")
        repos.extend(file_repos)
        skipped.extend(file_skipped)
