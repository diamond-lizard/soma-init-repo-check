#!/usr/bin/env python3
"""API phase: session setup, repo checking, output writing, summary."""
from __future__ import annotations

from typing import Any


def run_api_phase(
    repos: list[dict[str, str]],
    results: list[dict[str, Any]],
    errors: list[dict[str, str]],
    output_file: str,
    emacs_dir: str,
    init_count: int,
    quiet: bool,
    token: str,
) -> None:
    """Run the API checking phase with interrupt handling.

    Creates the cached session, emits progress for skipped repos,
    runs API checks, writes output, and prints the summary.
    Wraps the API loop in a KeyboardInterrupt handler that writes
    partial results via the signal handler.

    Input: repos -- validated GitHub repos for API checking.
           results -- skipped/config results so far.
           errors -- all errors so far.
           output_file -- path or '-' for stdout.
           emacs_dir -- for cache path computation.
           init_count -- for summary display.
           quiet -- suppress progress and summary if True.
           token -- GitHub personal access token.
    Output: None. Writes JSON output and prints summary.
    """
    from soma_init_repo_check.api_request import get_requested_urls
    from soma_init_repo_check.auth import GitHubTokenAuth
    from soma_init_repo_check.cache import cleanup_stale_entries
    from soma_init_repo_check.check_loop import check_all_repos
    from soma_init_repo_check.output_assembly import assemble_output
    from soma_init_repo_check.pipeline_skip import (
        count_not_github, emit_skipped_progress,
    )
    from soma_init_repo_check.progress import emit_skipping
    from soma_init_repo_check.session import compute_cache_path, create_session
    from soma_init_repo_check.signal_handler import handle_interrupt
    from soma_init_repo_check.summary import compute_summary, print_summary
    from soma_init_repo_check.writer import write_output

    auth = GitHubTokenAuth(token)
    cache_path = compute_cache_path(emacs_dir)
    session = create_session(cache_path, auth)

    not_github = count_not_github(results)
    total = len(repos) + not_github
    counter = emit_skipped_progress(results, total, quiet, emit_skipping)

    try:
        check_all_repos(
            repos, results, errors, session,
            output_file, total, counter, quiet,
        )
    except KeyboardInterrupt:
        handle_interrupt(
            output_file, results, errors, init_count, quiet,
        )
        return

    data = assemble_output(results, errors)
    write_output(output_file, data)
    cleanup_stale_entries(session, get_requested_urls())
    if not quiet:
        counters = compute_summary(init_count, results, errors)
        print_summary(counters)
