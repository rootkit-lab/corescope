# Makefile base para projetos C de sistemas — native + cross-compile (mingw).
# Contrato de targets (deve bater com .cursor/skills/dev-environment-setup/SKILL.md):
#   make install  — prepara deps (Unity, OpenSSL se TLS on)
#   make dev      — build debug + roda o binário local
#   make verify   — format check + lint + static analysis + build + test (gate do CI)
#   make build    — build de release (native ou cross conforme CROSS)
#   make dist     — empacota o artefato (zip)
#   make release  — aciona a skill release-changelog
#   make test     — só os testes (Unity)
#   make clean     — remove build artifacts

# === Configuração padrão ===
PROJECT ?= app
VERSION ?= 0.0.0

# Usar bash em receitas (process substitution, $(...), etc.)
SHELL := /bin/bash
.SHELLFLAGS := -c

# Diretórios
BUILD_DIR ?= build
OBJ_DIR   ?= $(BUILD_DIR)/obj
DIST_DIR  ?= dist
TEST_DIR  ?= tests

# Toolchain (native por padrão; CROSS=mingw seleciona cross-compile)
CC      ?= cc
CFLAGS  ?= -std=c11 -Wall -Wextra -Werror -O2
LDFLAGS ?=

# Cross-compile para Windows via mingw-w64
ifeq ($(CROSS),mingw)
  CC      := x86_64-w64-mingw32-gcc
  CFLAGS  += -D_WIN32_WINNT=0x0601
  LDFLAGS += -lws2_32
  EXE_EXT := .exe
else
  EXE_EXT :=
endif

# Feature flags (1 = habilita, 0 = usa stub)
WINDOWS_TLS ?= 0

# === Fontes ===
SRC_DIRS := src
SOURCES  := $(shell find $(SRC_DIRS) -name '*.c' 2>/dev/null)
HEADERS  := $(shell find include -name '*.h' 2>/dev/null)

# Seleção de stub: se WINDOWS_TLS=0, usa transport_tls_stub.c; senão transport_tls.c
ifeq ($(WINDOWS_TLS),1)
  TLS_SRC := src/transport/transport_tls.c
  TLS_CFLAGS := -Ithird_party/openssl-mingw/prefix/include
  TLS_LDFLAGS := -Lthird_party/openssl-mingw/prefix/lib -lssl -lcrypto
  ifeq ($(CROSS),mingw)
    TLS_LDFLAGS += -lcrypt32 -lws2_32
  endif
else
  TLS_SRC := src/transport/transport_tls_stub.c
  TLS_CFLAGS := -DNO_TLS_STUB
  TLS_LDFLAGS :=
endif

# Remove a opção não selecionada das SOURCES (evita linkar os dois)
TLS_STUB_SRC := src/transport/transport_tls_stub.c
TLS_REAL_SRC := src/transport/transport_tls.c
SOURCES := $(filter-out $(TLS_STUB_SRC) $(TLS_REAL_SRC),$(SOURCES)) $(TLS_SRC)

OBJECTS := $(patsubst %.c,$(OBJ_DIR)/%.o,$(SOURCES))
BINARY  := $(BUILD_DIR)/$(PROJECT)$(EXE_EXT)

# === Testes (Unity) ===
UNITY_DIR    := $(TEST_DIR)/unity
TEST_SOURCES := $(shell find $(TEST_DIR) -name 'test_*.c' 2>/dev/null)
TEST_BINARY  := $(BUILD_DIR)/test_runner

.PHONY: install dev verify build dist release test clean help

help:
	@echo "Targets:"
	@echo "  make install          — prepara deps (Unity via scripts/, OpenSSL via scripts/)"
	@echo "  make dev              — build debug + roda local"
	@echo "  make verify           — gate: format + lint + tidy + cppcheck + build + test"
	@echo "  make build            — build de release (CROSS=mingw para Windows)"
	@echo "  make dist             — empacota zip em $(DIST_DIR)/"
	@echo "  make test             — só os testes Unity"
	@echo "  make release VERSION=X.Y.Z — aciona release-changelog"
	@echo "  make clean            — remove $(BUILD_DIR) e $(DIST_DIR)"
	@echo ""
	@echo "Variáveis úteis:"
	@echo "  CROSS=mingw           — cross-compile para Windows"
	@echo "  WINDOWS_TLS=1         — usa OpenSSL (requer third_party/openssl-mingw)"
	@echo "  CC=clang CFLAGS=...   — override do toolchain"

install:
	@if [ ! -f "$(UNITY_DIR)/unity.h" ]; then \
	  echo "Baixando Unity (framework de testes)..."; \
	  bash scripts/build-unity.sh; \
	fi
	@if [ "$(WINDOWS_TLS)" = "1" ] && [ ! -d third_party/openssl-mingw/prefix ]; then \
	  echo "ATENÇÃO: WINDOWS_TLS=1 mas third_party/openssl-mingw/prefix não existe." >&2; \
	  echo "  Rode: scripts/build-openssl-mingw.sh" >&2; \
	  exit 1; \
	fi

dev: CFLAGS := $(filter-out -O2,$(CFLAGS)) -g -DDEBUG
dev: build
	./$(BINARY)

verify: install format-check lint tidy cppcheck build test

build: $(BINARY)

$(BINARY): $(OBJECTS)
	@mkdir -p $(dir $@)
	$(CC) $(OBJECTS) $(TLS_LDFLAGS) $(LDFLAGS) -o $@

$(OBJ_DIR)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $(TLS_CFLAGS) -Iinclude -c $< -o $@

# === Testes ===
test: install $(TEST_BINARY)
	./$(TEST_BINARY)

$(TEST_BINARY): $(filter-out src/core/main.c,$(SOURCES)) $(TEST_SOURCES) $(UNITY_DIR)/unity.c $(UNITY_DIR)/unity.h
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -D_POSIX_C_SOURCE=200112L -Iinclude -I$(UNITY_DIR) -DTEST \
	  $(filter-out src/core/main.c,$(SOURCES)) $(TEST_SOURCES) $(UNITY_DIR)/unity.c \
	  -o $@

# === Gates de qualidade ===
format-check:
	@if command -v clang-format >/dev/null 2>&1; then \
	  rc=0; \
	  for f in $(SOURCES) $(HEADERS); do \
	    if ! diff -q <(cat "$$f") <(clang-format "$$f") >/dev/null 2>&1; then \
	      echo "FORMAT: $$f não está formatado (rode: make format)"; \
	      rc=1; \
	    fi; \
	  done; \
	  if [ $$rc -eq 0 ]; then echo "format OK"; else exit 1; fi; \
	else \
	  echo "aviso: clang-format não instalado, pulando format-check"; \
	fi

format:
	clang-format -i $(SOURCES) $(HEADERS)

lint:
	@command -v cppcheck >/dev/null 2>&1 && cppcheck --enable=warning,style --error-exitcode=1 --suppress=missingIncludeSystem $(SRC_DIRS) || echo "aviso: cppcheck não instalado, pulando lint"

tidy:
	@command -v clang-tidy >/dev/null 2>&1 && \
	  clang-tidy $(SOURCES) -- -std=c11 -Iinclude $(TLS_CFLAGS) || \
	  echo "aviso: clang-tidy não instalado, pulando tidy"

cppcheck:
	@command -v cppcheck >/dev/null 2>&1 && cppcheck --enable=all --error-exitcode=1 --suppress=missingIncludeSystem $(SRC_DIRS) || true

# === Distribuição ===
dist: build
	mkdir -p $(DIST_DIR)
	cp $(BINARY) $(DIST_DIR)/
	@if [ -f config.yml.example ]; then cp config.yml.example $(DIST_DIR)/; fi
	cd $(DIST_DIR) && zip -q $(PROJECT)-$(VERSION).zip $(notdir $(BINARY)) $(addprefix ,$(wildcard config.yml.example))
	@echo "Artefato em $(DIST_DIR)/$(PROJECT)-$(VERSION).zip"

release:
	.cursor/skills/release-changelog/scripts/prepare-release.sh --version $(VERSION)

clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR)
