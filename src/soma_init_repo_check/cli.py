#!/usr/bin/env python3
"""CLI entry point for soma-init-repo-check."""
from __future__ import annotations

import sys

import click


@click.command()
@click.argument("output_file")
@click.option("--emacs-dir", default="~/.emacs.d/", help="Path to Emacs directory.")
@click.option("--output-format", default="json", type=click.Choice(["json"]), help="Output format.")
@click.option("--quiet", is_flag=True, help="Suppress progress and summary output.")
def main(output_file: str, emacs_dir: str, output_format: str, quiet: bool) -> None:
    """Check if GitHub forks used in Emacs config are behind upstream.

    OUTPUT_FILE is the path to write JSON results, or - for stdout.
    """
    click.echo(f"soma-init-repo-check: not yet implemented (output={output_file})", err=True)
    sys.exit(1)
