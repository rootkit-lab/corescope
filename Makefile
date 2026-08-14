.PHONY: install dev verify build dist skill release clean

VERSION ?= 0.0.0
PY ?= python3
VENV ?= .venv

install:
	$(PY) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -e ".[dev]"

dev:
	$(VENV)/bin/corescope --help

verify:
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/pytest

build:
	@echo "Projetos Python normalmente nao tem 'build' de binario — ver 'dist' para empacotamento."

dist: build
	$(VENV)/bin/pip install --quiet build
	$(VENV)/bin/python -m build
	$(VENV)/bin/python skill/package_skill.py skill/corescope --output releases/

skill:
	$(VENV)/bin/python skill/package_skill.py skill/corescope --output releases/

release:
	.cursor/skills/release-changelog/scripts/prepare-release.sh --version $(VERSION)

clean:
	rm -rf dist/ build/ *.egg-info releases/ $(VENV)
