.PHONY: install dev verify build dist release clean

VERSION ?= 0.0.0

install:
	npm ci

dev:
	npm run dev

verify:
	npm run lint
	npx tsc --noEmit
	npm run build
	npm test --if-present

build:
	npm run build

dist: build
	@echo "Artefato em dist/ — empacotar (imagem Docker) conforme deploy-setup."

release:
	.cursor/skills/release-changelog/scripts/prepare-release.sh --version $(VERSION)

clean:
	rm -rf dist/ node_modules/.cache
