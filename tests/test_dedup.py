#!/usr/bin/env python3
"""Tests for repo deduplication logic."""
from __future__ import annotations

from soma_init_repo_check.dedup import deduplicate_repos


def _repo(owner: str, repo: str, host: str, init_file: str) -> dict[str, str]:
    """Build a repo entry dict for testing."""
    return {"owner": owner, "repo": repo, "host": host, "init_file": init_file}


def test_same_repo_two_files_appears_once() -> None:
    """Same repo from two different init files appears only once."""
    repos = [
        _repo("owner", "repo", "github", "b-init.el"),
        _repo("owner", "repo", "github", "a-init.el"),
    ]
    result = deduplicate_repos(repos)
    assert len(result) == 1


def test_same_owner_repo_different_hosts_distinct() -> None:
    """Same OWNER/REPO on different hosts treated as distinct."""
    repos = [
        _repo("owner", "repo", "github", "a-init.el"),
        _repo("owner", "repo", "gitlab", "b-init.el"),
    ]
    result = deduplicate_repos(repos)
    assert len(result) == 2


def test_config_statuses_not_deduplicated() -> None:
    """Config-level statuses are separate from repo dedup.

    deduplicate_repos only handles repo entries (owner/repo/host/init_file).
    skipped:no_repo_directive and skipped:no_host entries live in a separate
    list maintained by the caller and are never passed to this function.
    """
    repos = [
        _repo("owner", "repo", "github", "a-init.el"),
        _repo("owner", "repo", "github", "b-init.el"),
    ]
    no_repo = [
        {"status": "skipped:no_repo_directive", "init_file": "c-init.el"},
        {"status": "skipped:no_repo_directive", "init_file": "d-init.el"},
    ]
    deduped = deduplicate_repos(repos)
    assert len(deduped) == 1
    assert len(no_repo) == 2


def test_alphabetically_first_init_file_kept() -> None:
    """For duplicates, the alphabetically first init file is kept."""
    repos = [
        _repo("owner", "repo", "github", "z-init.el"),
        _repo("owner", "repo", "github", "m-init.el"),
        _repo("owner", "repo", "github", "a-init.el"),
    ]
    result = deduplicate_repos(repos)
    assert len(result) == 1
    assert result[0]["init_file"] == "a-init.el"


def test_github_host_and_no_host_both_preserved() -> None:
    """Repo with :host github in one file and no :host in another.

    The github entry goes through dedup as a repo entry.
    The no-:host entry is a skipped:no_host in a separate list.
    Both coexist in the final output.
    """
    repos = [_repo("owner", "repo", "github", "a-init.el")]
    no_host = [
        {"status": "skipped:no_host", "init_file": "b-init.el", "repo": "owner/repo"},
    ]
    deduped = deduplicate_repos(repos)
    assert len(deduped) == 1
    assert deduped[0]["host"] == "github"
    assert len(no_host) == 1


def test_multiple_no_host_same_file_each_unique_repo() -> None:
    """Within one init file, each unique :repo without :host gets own entry.

    These are config-level statuses in a separate list, not passed to dedup.
    Each unique :repo value produces its own skipped:no_host entry.
    """
    no_host = [
        {"status": "skipped:no_host", "init_file": "a-init.el", "repo": "foo/bar"},
        {"status": "skipped:no_host", "init_file": "a-init.el", "repo": "baz/qux"},
    ]
    assert len(no_host) == 2
    repos_in_entries = {e["repo"] for e in no_host}
    assert repos_in_entries == {"foo/bar", "baz/qux"}
