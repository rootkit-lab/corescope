.PHONY: install dev verify build dist release clean

BINARY ?= app
VERSION ?= 0.0.0

install:
	go mod download
	cd web && npm ci

dev:
	@echo "Rodando backend com hot-reload (ajustar para air/reflex se preferir) e frontend Vite em paralelo:"
	@echo "  terminal 1: go run ./cmd/$(BINARY)"
	@echo "  terminal 2: cd web && npm run dev"
	go run ./cmd/$(BINARY)

verify:
	gofmt -l . | tee /tmp/gofmt-out; test ! -s /tmp/gofmt-out
	go vet ./...
	cd web && npm run build
	go build -o /tmp/$(BINARY)-verify ./cmd/$(BINARY)
	go test ./...

build:
	cd web && npm run build
	go build -trimpath -ldflags="-s -w -X main.version=$(VERSION)" -o bin/$(BINARY) ./cmd/$(BINARY)

dist: build
	@echo "Artefato em bin/$(BINARY) — empacotar (tar.gz/deb/instalador) conforme deploy-setup."

release:
	.cursor/skills/release-changelog/scripts/prepare-release.sh --version $(VERSION)

clean:
	rm -rf bin/ web/dist/
