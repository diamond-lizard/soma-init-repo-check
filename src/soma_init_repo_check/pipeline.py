#!/usr/bin/env python3
"""Orchestration pipeline for soma-init-repo-check."""
from __future__ import annotations

from soma_init_repo_check.types import ErrorEntry, RepoInfo, ResultEntry


def run_pipeline(
    output_file: str, emacs_dir: str, quiet: bool,
) -> None:
    """Run the full check pipeline: parse, validate, check, output.

    Executes all local work (steps 2-7) before any API calls.

    Input: output_file -- path or '-' for stdout.
           emacs_dir -- Emacs directory path.
           quiet -- suppress progress and summary if True.
    Output: None. Writes JSON results. Exits on fatal errors.
    """
    from soma_init_repo_check.auth import retrieve_token, validate_token
    from soma_init_repo_check.dedup import deduplicate_repos
    from soma_init_repo_check.init_parser import (
        extract_elpaca_repo_url, extract_soma_inits, read_init_el,
    )
    from soma_init_repo_check.pipeline_local import collect_all_repos
    from soma_init_repo_check.url_parser import parse_repo_url
    from soma_init_repo_check.writer_check import check_output_exists

    check_output_exists(output_file)
    token = retrieve_token()
    validate_token(token)
    tree = read_init_el(emacs_dir)
    elpaca_url = extract_elpaca_repo_url(tree)
    soma_inits = extract_soma_inits(tree)
    owner, repo, host_id, is_github = parse_repo_url(elpaca_url)
    repos, skipped, errors = collect_all_repos(
        soma_inits, emacs_dir, owner, repo, host_id, is_github,
    )
    deduped = deduplicate_repos(repos)
    valid, val_errors = _validate_all_repos(deduped)
    errors.extend(val_errors)
    all_results: list[ResultEntry] = list(skipped)
    _run_api_and_output(
        valid, all_results, errors, output_file,
        emacs_dir, len(soma_inits), quiet, token,
    )


def _validate_all_repos(
    repos: list[RepoInfo],
) -> tuple[list[RepoInfo], list[ErrorEntry]]:
    """Validate OWNER/REPO strings, separating valid from invalid.

    Input: repos -- list of repo dicts with owner/repo keys.
    Output: (valid_repos, validation_error_entries).
    """
    from soma_init_repo_check.output import validation_error_entry
    from soma_init_repo_check.validation import validate_owner_repo

    valid: list[RepoInfo] = []
    val_errors: list[ErrorEntry] = []
    for entry in repos:
        owner_repo = f"{entry['owner']}/{entry['repo']}"
        err = validate_owner_repo(owner_repo)
        if err:
            val_errors.append(validation_error_entry(owner_repo, err))
        else:
            valid.append(entry)
    return valid, val_errors


def _run_api_and_output(
    repos: list[RepoInfo],
    results: list[ResultEntry],
    errors: list[ErrorEntry],
    output_file: str,
    emacs_dir: str,
    init_count: int,
    quiet: bool,
    token: str,
) -> None:
    """Create session, run API checks, write output, print summary.

    Wraps the API loop in a KeyboardInterrupt handler that writes
    partial results. Emits skip-format progress for not_github repos,
    then check-format progress for each API-checked repo.

    Input: repos -- validated GitHub repos for API checking.
           results -- skipped/config results so far.
           errors -- all errors so far. output_file -- path or '-'.
           emacs_dir -- for cache path. init_count -- for summary.
           quiet -- suppress output. token -- GitHub API token.
    Output: None. Writes JSON output and prints summary.
    """
    from soma_init_repo_check.pipeline_api import run_api_phase

    run_api_phase(
        repos, results, errors, output_file,
        emacs_dir, init_count, quiet, token,
    )
