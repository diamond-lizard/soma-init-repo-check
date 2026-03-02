#!/usr/bin/env python3
"""Cache maintenance: cleanup of stale entries after a successful run."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests_cache


def cleanup_stale_entries(
    session: requests_cache.CachedSession,
    requested_urls: frozenset[str],
) -> None:
    """Delete cached responses for URLs not requested in the current run.

    Compares the set of all cached URLs against the URLs requested
    during this run. Any cached URL not in the requested set is
    considered stale and is deleted. This prevents unbounded cache
    growth when repos are removed from the Emacs configuration.

    Must only be called after a successful (non-interrupted) run.

    Input: session -- the CachedSession used for API calls.
           requested_urls -- frozenset of URLs requested this run.
    Output: None. Deletes stale cache entries as a side effect.
    """
    cached_urls = set(session.cache.urls())
    stale_urls = cached_urls - requested_urls
    if stale_urls:
        session.cache.delete(urls=list(stale_urls))
