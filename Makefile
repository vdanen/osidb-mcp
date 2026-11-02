# osidb-mcp — development and releases (same release targets as pymnifocus).
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

PYTHON       ?= .venv/bin/python
UV           ?= uv
BREW_TAP     ?= ../homebrew-osidb-mcp
PIP          := $(PYTHON) -m pip
PYTEST_ARGS  ?=

.PHONY: help install sync test livetest test-uv audit check build clean publish upload version show-version dev brew

help:
	@echo "osidb-mcp — common targets"
	@echo "  make install   # pip install -e \".[dev]\" (same idea as CI)"
	@echo "  make dev       # install dev dependencies with uv (also: make sync)"
	@echo "  make test      # pytest (unit/offline tests under tests/ only)"
	@echo "  make livetest  # optional integration tests vs real OSIDB (-vv -s count lines; see live_tests/README.md)"
	@echo "  make test-uv   # $(UV) run pytest (tests/ only)"
	@echo "  make audit     # pip-audit (current environment)"
	@echo "  make check     # test + audit"
	@echo "  make build     # sdist + wheel under dist/"
	@echo "  make clean     # remove build artifacts"
	@echo "  make publish   # emergency manual upload via uv (also: make upload)"
	@echo "  make version VERSION=x.y.z # bump version, commit, and create local tag"
	@echo "  make show-version # print package version"
	@echo "  make brew      # generate formula from PyPI and copy to $(BREW_TAP)"

install:
	$(PIP) install -U pip
	$(PIP) install -e ".[dev]"

dev: sync

sync:
	$(UV) sync --extra dev

test:
	$(PYTHON) -m pytest tests $(PYTEST_ARGS)

livetest:
	$(PYTHON) -m pytest live_tests -vv -s $(PYTEST_ARGS)

test-uv:
	$(UV) run pytest tests $(PYTEST_ARGS)

audit:
	$(PYTHON) -m pip_audit

check: test audit

build: clean
	$(UV) build

clean:
	rm -rf dist/ build/ .eggs/
	rm -rf src/*.egg-info *.egg-info
	rm -rf .pytest_cache

publish: build
	@echo "Prefer Trusted Publishing: push a release tag on main. Manual upload requires PyPI credentials."
	$(UV) publish

upload: publish

version:
ifndef VERSION
	$(error VERSION is required. Usage: make version VERSION=1.2.3)
endif
	@git diff --cached --quiet || { echo "Commit or unstage existing staged changes first." >&2; exit 1; }
	@if git show-ref --verify --quiet "refs/tags/v$(VERSION)"; then echo "Tag v$(VERSION) already exists." >&2; exit 1; fi
	@$(PYTHON) -c 'import re,sys; assert re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", sys.argv[1]), "VERSION must be x.y.z"' "$(VERSION)"
	$(UV) version --no-sync "$(VERSION)"
	$(PYTHON) -c 'import pathlib,re,sys; p=pathlib.Path("src/osidb_mcp/__init__.py"); p.write_text(re.sub(r"^__version__ = .*$$", "__version__ = " + repr(sys.argv[1]), p.read_text(), flags=re.M))' "$$($(UV) version --short)"
	git add pyproject.toml uv.lock src/osidb_mcp/__init__.py
	git commit -m "Bump version to $(VERSION)"
	git tag -a "v$(VERSION)" -m "v$(VERSION)"
	@echo ""
	@echo "Created commit and local tag v$(VERSION). Next steps:"
	@echo "  1. git push origin main"
	@echo "  2. git push origin v$(VERSION)"
	@echo "  3. Approve the pypi environment deployment in Actions if prompted."
	@echo "  4. Confirm https://pypi.org/project/osidb-mcp/ then run make brew."

show-version:
	@$(UV) version --short


brew: ## Generate Homebrew formula (requires package on PyPI)
	@mkdir -p Formula
	@VERSION=$$(grep '^version' pyproject.toml | sed 's/.*"\(.*\)"/\1/') && \
	METADATA=$$(curl -sfL "https://pypi.org/pypi/osidb-mcp/$$VERSION/json" | \
		$(PYTHON) -c "import json,sys;d=json.load(sys.stdin);u=next(x for x in d['urls'] if x['filename'].endswith('.tar.gz'));print(u['url'], u['digests']['sha256'])") && \
	read -r URL SHA <<< "$$METADATA" || \
	{ echo "Error: osidb-mcp $$VERSION not found on PyPI. Push the release tag and wait for Trusted Publishing first." >&2; exit 1; } && \
	sed -e "s|@@URL@@|$$URL|g" -e "s|@@SHA256@@|$$SHA|g" \
		Formula/osidb-mcp.rb.in > Formula/osidb-mcp.rb && \
	echo "==> Formula/osidb-mcp.rb (version $$VERSION)" && \
	echo "    Install locally:  brew install --formula Formula/osidb-mcp.rb" && \
	echo "    For a tap: copy Formula/osidb-mcp.rb to your homebrew-tap repo"
	rsync -avz Formula/osidb-mcp.rb "$(BREW_TAP)/Formula/osidb-mcp.rb"
