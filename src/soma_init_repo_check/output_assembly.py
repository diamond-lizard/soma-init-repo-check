#!/usr/bin/env python3
"""Assemble the final JSON output structure."""
from __future__ import annotations

from typing import Any

from soma_init_repo_check.output_sort import sort_errors
from soma_init_repo_check.output_sort import sort_results


def assemble_output(
    results: list[dict[str, Any]],
    errors: list[dict[str, str]],
    interrupted: bool = False,
) -> dict[str, Any]:
    """Assemble the final JSON output with sorted results and errors.

    The output has two required top-level keys ('results' and 'errors').
    When interrupted is True, adds 'interrupted': true. When False,
    the 'interrupted' key is absent.

    Input: results -- list of result entry dicts.
           errors -- list of error entry dicts.
           interrupted -- whether the run was interrupted.
    Output: dict ready for json.dumps with sorted arrays.
    """
    output: dict[str, Any] = {
        "results": sort_results(results),
        "errors": sort_errors(errors),
    }
    if interrupted:
        output["interrupted"] = True
    return output
