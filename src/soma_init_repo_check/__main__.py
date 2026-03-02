#!/usr/bin/env python3
"""Entry point for python -m soma_init_repo_check."""
from __future__ import annotations
import os

from soma_init_repo_check.cli import main

main(prog_name=os.environ.get("SOMA_PROG_NAME"))
