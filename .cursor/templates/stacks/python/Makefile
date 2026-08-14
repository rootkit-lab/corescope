.PHONY: install dev verify build dist release clean

VERSION ?= 0.0.0
PY ?= python3
VENV ?= .venv

install:
	$(PY) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt -r requirements-dev.txt

dev:
	$(VENV)/bin/python -m src.main

verify:
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/pytest

build:
	@echo "Projetos Python normalmente não têm 'build' de binário — ver dist/release para empacotamento."

dist:
	$(VENV)/bin/pip install build
	$(VENV)/bin/python -m build

release:
	.cursor/skills/release-changelog/scripts/prepare-release.sh --version $(VERSION)

clean:
	rm -rf dist/ build/ *.egg-info $(VENV)
