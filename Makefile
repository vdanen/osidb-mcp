# osidb-mcp — local dev, CI parity, build, PyPI upload
#
# Defaults match .github/workflows/ci.yml (pip + editable install).
# Optional: `make sync` / `make test-uv` if you use uv (uv.lock present).

PYTHON       ?= python3
PIP          := $(PYTHON) -m pip
PYTEST_ARGS  ?=
TWINE        := $(PYTHON) -m twine

.PHONY: help install sync test test-uv audit check build clean upload version

help:
	@echo "osidb-mcp — common targets"
	@echo "  make install   # pip install -e \".[dev]\" (same idea as CI)"
	@echo "  make sync      # uv sync --extra dev (requires uv)"
	@echo "  make test      # pytest"
	@echo "  make test-uv   # uv run pytest"
	@echo "  make audit     # pip-audit (current environment)"
	@echo "  make check     # test + audit"
	@echo "  make build     # sdist + wheel under dist/"
	@echo "  make clean     # remove build artifacts"
	@echo "  make upload    # twine check + upload dist/* (needs twine + credentials)"
	@echo "  make version   # print package version (no OSIDB needed)"

install:
	$(PIP) install -U pip
	$(PIP) install -e ".[dev]"

sync:
	uv sync --extra dev

test:
	$(PYTHON) -m pytest $(PYTEST_ARGS)

test-uv:
	uv run pytest $(PYTEST_ARGS)

audit:
	$(PYTHON) -m pip_audit

check: test audit

build:
	$(PIP) install -q build
	$(PYTHON) -m build

clean:
	rm -rf dist/ build/ .eggs/
	rm -rf src/*.egg-info *.egg-info
	rm -rf .pytest_cache

upload: build
	$(PIP) install -q twine
	$(TWINE) check dist/*
	$(TWINE) upload dist/*

version:
	@$(PYTHON) -m osidb_mcp --version
