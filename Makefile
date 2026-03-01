.DEFAULT_GOAL := help

.PHONY: help ruff ruff-fix mypy test

help:
	@echo "Available targets:"
	@echo "  ruff      - Run ruff linter"
	@echo "  ruff-fix  - Run ruff with auto-fix"
	@echo "  mypy      - Run mypy type checker"
	@echo "  test      - Run ruff, mypy, then pytest"

ruff:
	ruff check src/ tests/

ruff-fix:
	ruff check --fix src/ tests/

mypy:
	mypy src/

test: ruff mypy
	pytest tests/
