#!/usr/bin/env python3
"""TypedDict definitions for structured data used across the project."""
from __future__ import annotations

from typing import TypedDict


class ForkResult(TypedDict):
    """Result for a fork repo with ahead/behind counts."""

    status: str
    repo_url: str
    ahead_by: int
    behind_by: int


class SkippedNotAForkResult(TypedDict):
    """Result for a repo that is not a fork."""

    status: str
    repo_url: str


class SkippedNotGithubResult(TypedDict):
    """Result for a repo not hosted on GitHub."""

    status: str
    repo: str
    host: str


class SkippedNoRepoResult(TypedDict):
    """Result for an init file with no :repo directive."""

    status: str
    init_file: str


class SkippedNoHostResult(TypedDict):
    """Result for an init file with :repo but no :host."""

    status: str
    init_file: str
    repo: str


class ErrorEntry(TypedDict):
    """An error encountered during processing."""

    repo_url: str
    error: str


class RepoInfo(TypedDict):
    """Parsed repo information from an init file."""

    owner: str
    repo: str
    host: str
    init_file: str


class OutputData(TypedDict, total=False):
    """Top-level JSON output structure."""

    results: list[ForkResult | SkippedNotAForkResult | SkippedNotGithubResult | SkippedNoRepoResult | SkippedNoHostResult]
    errors: list[ErrorEntry]
    interrupted: bool
