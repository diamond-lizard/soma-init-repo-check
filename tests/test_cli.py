#!/usr/bin/env python3
"""Tests for CLI argument handling."""
from __future__ import annotations

from click.testing import CliRunner

from soma_init_repo_check.cli import main


def test_no_arguments_produces_usage_error() -> None:
    """Calling with no arguments produces exit code 2."""
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 2


def test_help_prints_usage_and_exits_zero() -> None:
    """--help prints usage information and exits with code 0."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "OUTPUT_FILE" in result.output
    assert "--emacs-dir" in result.output
    assert "--quiet" in result.output


def test_quiet_flag_is_accepted() -> None:
    """--quiet flag is accepted without error by the CLI parser."""
    runner = CliRunner()
    result = runner.invoke(main, ["--quiet", "--help"])
    assert result.exit_code == 0


def test_emacs_dir_accepts_custom_path() -> None:
    """--emacs-dir accepts a custom path."""
    runner = CliRunner()
    result = runner.invoke(main, ["--emacs-dir", "/tmp/test", "--help"])
    assert result.exit_code == 0


def test_output_format_json_is_accepted() -> None:
    """--output-format json is accepted."""
    runner = CliRunner()
    result = runner.invoke(main, ["--output-format", "json", "--help"])
    assert result.exit_code == 0


def test_invalid_output_format_is_rejected() -> None:
    """An invalid --output-format value is rejected with exit code 2."""
    runner = CliRunner()
    result = runner.invoke(main, ["--output-format", "xml", "out.json"])
    assert result.exit_code == 2
    assert "xml" in result.output or "Invalid" in result.output


def test_existing_output_file_produces_error(tmp_path: object) -> None:
    """Calling with an existing OUTPUT_FILE path produces exit code 1."""
    from pathlib import Path

    outfile = Path(str(tmp_path)) / "existing.json"
    outfile.write_text("{}")
    runner = CliRunner()
    result = runner.invoke(main, [str(outfile)])
    assert result.exit_code == 1
    assert "already exists" in result.output
