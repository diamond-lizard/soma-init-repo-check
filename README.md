# soma-init-repo-check

A command-line tool that checks whether GitHub forks referenced in an Emacs
configuration are behind their upstream repositories.

## Overview

`soma-init-repo-check` parses an Emacs `init.el` file and its associated
soma init files to extract all GitHub repository references. It then queries
the GitHub API to determine the fork status of each repository, reporting
how many commits each fork is ahead of or behind its upstream parent.

The tool is designed for Emacs configurations that use
[elpaca](https://github.com/progfolio/elpaca) as a package manager and
organize package configurations into per-package init files via a
`soma-inits` variable.

## What it does

1. Reads `init.el` from the Emacs directory (default `~/.emacs.d/`)
2. Extracts the elpaca bootstrap `:repo` URL
3. Extracts the `soma-inits` symbol list (per-package init file names)
4. Reads each soma init `.el` file and extracts `:repo` and `:host` directives
5. Deduplicates and validates all discovered repositories
6. Queries the GitHub API for each repository's fork status
7. For forks, compares the fork's default branch against the upstream default branch
8. Writes a JSON report with the results

## Requirements

- Python 3.12+
- A GitHub personal access token stored in [pass](https://www.passwordstore.org/)
  at `github.com/fgpat/public-repos-only`
- An Emacs configuration with `elpaca-order` and `soma-inits` definitions in
  `init.el`

## Installation

```sh
git clone https://github.com/diamond-lizard/soma-init-repo-check.git
cd soma-init-repo-check
uv sync
```

## Usage

```
soma-init-repo-check [OPTIONS] OUTPUT_FILE
```

`OUTPUT_FILE` is the path to write JSON results, or `-` for stdout.

### Options

| Option             | Default       | Description                            |
| ------------------ | ------------- | -------------------------------------- |
| `--emacs-dir`      | `~/.emacs.d/` | Path to the Emacs directory            |
| `--output-format`  | `json`        | Output format (currently only `json`)  |
| `--quiet`          | off           | Suppress progress and summary output   |
| `--help`           |               | Show help message                      |

### Examples

Write results to a file:

```sh
soma-init-repo-check results.json
```

Write results to stdout:

```sh
soma-init-repo-check -
```

Use a custom Emacs directory and suppress progress output:

```sh
soma-init-repo-check --emacs-dir ~/my-emacs/ --quiet results.json
```

### Running via the wrapper script

A shell wrapper is provided at `bin/soma-init-repo-check` that activates the
project virtualenv automatically:

```sh
bin/soma-init-repo-check results.json
```

### Running as a Python module

```sh
python -m soma_init_repo_check results.json
```

## Output format

The tool writes a JSON object with `results` and `errors` arrays. If the run
is interrupted with Ctrl-C, partial results are written with an `interrupted`
flag set to `true`.

### Result entry types

| Status                       | Fields                                     | Meaning                                  |
| ---------------------------- | ------------------------------------------ | ---------------------------------------- |
| `fork`                       | `repo_url`, `ahead_by`, `behind_by`        | Fork with commit comparison counts       |
| `skipped:not_a_fork`         | `repo_url`                                 | Repository is not a fork                 |
| `skipped:not_github`         | `repo`, `host`, `init_file`                | Repository is not hosted on GitHub       |
| `skipped:no_repo_directive`  | `init_file`                                | Init file has no `:repo` directive       |
| `skipped:no_host`            | `init_file`, `repo`                        | Init file has `:repo` but no `:host`     |

### Error entry types

| Type             | Fields               | Meaning                              |
| ---------------- | -------------------- | ------------------------------------ |
| API error        | `repo_url`, `error`  | GitHub API or network failure        |
| Init file error  | `init_file`, `error` | Missing, oversized, or unparseable   |
| Validation error | `repo`, `error`      | Invalid OWNER/REPO string            |

### Example output

```json
{
  "results": [
    {
      "status": "fork",
      "repo_url": "https://github.com/user/some-package",
      "ahead_by": 3,
      "behind_by": 12
    },
    {
      "status": "skipped:not_a_fork",
      "repo_url": "https://github.com/user/another-package"
    }
  ],
  "errors": []
}
```

## Caching

API responses are cached in a SQLite database using
[requests-cache](https://requests-cache.readthedocs.io/) with ETag-based
conditional requests. The cache is stored at:

```
$XDG_CACHE_HOME/soma-init-repo-check/etags/<hash>.sqlite
```

where `<hash>` is derived from the resolved Emacs directory path. Cache
entries for repositories no longer in the configuration are automatically
cleaned up after each successful run.

## Rate limiting

The tool respects GitHub API rate limits by:

- Waiting the duration specified in `x-ratelimit-reset` or `retry-after` headers
- Applying a 100ms delay between requests to avoid secondary rate limits
- Retrying rate-limited requests with exponential backoff via
  [tenacity](https://tenacity.readthedocs.io/)

## Development

```sh
make help       # Show available targets
make test       # Run ruff, mypy, then pytest
make ruff       # Run ruff linter
make ruff-fix   # Run ruff with auto-fix
make mypy       # Run mypy type checker
```

## License

See the project repository for license information.
