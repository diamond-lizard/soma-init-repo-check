#!/usr/bin/env python3
"""Inner API checking loop for validated GitHub repos."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests_cache
    from soma_init_repo_check.types import ErrorEntry, RepoInfo, ResultEntry

from tenacity import RetryError

from soma_init_repo_check.check_one import check_one
from soma_init_repo_check.error_tracker import HostErrorTracker
from soma_init_repo_check.error_tracker import abort_threshold
from soma_init_repo_check.progress import emit_checking
from soma_init_repo_check.rate_abort import abort_rate_limit
from soma_init_repo_check.rate_limit import inter_request_delay

_HOST = "api.github.com"


def check_all_repos(
    repos: list[RepoInfo],
    results: list[ResultEntry],
    errors: list[ErrorEntry],
    session: requests_cache.CachedSession,
    output_file: str,
    total: int,
    counter: int,
    quiet: bool,
) -> None:
    """Check each repo via API, recording results and errors.

    Input: repos -- validated GitHub repos for API checking.
           results -- result accumulator list (mutated in place).
           errors -- error accumulator list (mutated in place).
           session -- CachedSession for API calls.
           output_file -- path or '-' for stdout.
           total -- total unique repo count for progress display.
           counter -- starting counter value for progress display.
           quiet -- suppress progress messages if True.
    Output: None. Mutates results and errors in place.
    """
    tracker = HostErrorTracker()
    for entry in repos:
        counter += 1
        owner_repo = f"{entry['owner']}/{entry['repo']}"
        if not quiet:
            emit_checking(counter, total, owner_repo)
        _process_one_repo(
            entry, session, tracker, results, errors,
            output_file, owner_repo, quiet,
        )
        inter_request_delay()


def _process_one_repo(
    entry: RepoInfo,
    session: requests_cache.CachedSession,
    tracker: HostErrorTracker,
    results: list[ResultEntry],
    errors: list[ErrorEntry],
    output_file: str,
    owner_repo: str,
    quiet: bool,
) -> None:
    """Process a single repo: API call, error tracking, threshold check.

    Calls check_one for the API interaction, appends results and
    errors, then tracks the error count against the per-host
    threshold. Aborts the run if rate limit retries are exhausted
    or the error threshold is exceeded.

    Input: entry -- repo dict with owner/repo keys.
           session -- CachedSession for API calls.
           tracker -- per-host error tracker.
           results -- result accumulator (mutated in place).
           errors -- error accumulator (mutated in place).
           output_file -- for abort messages.
           owner_repo -- "OWNER/REPO" string.
           quiet -- suppress output if True.
    Output: None. Mutates results, errors, and tracker.
    """
    owner, repo = entry["owner"], entry["repo"]
    try:
        res, err, n = check_one(session, owner, repo, owner_repo)
    except RetryError:
        abort_rate_limit(output_file, results, errors, quiet)
        return
    if res:
        results.append(res)
    if err:
        errors.append(err)
    if n > 0:
        tracker.add_errors(_HOST, n)
    if n > 0 and tracker.check_threshold(_HOST):
        abort_threshold(_HOST, output_file, results, errors, quiet)
