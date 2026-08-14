#!/usr/bin/env bash
# Bootstrap do Unity (framework de testes C da ThrowTheSwitch).
# Baixa versão pinada e coloca em tests/unity/.
# Uso: scripts/build-unity.sh   (chamado por `make install`)
# Pré-requisitos: curl, sha256sum.

set -euo pipefail

UNITY_VERSION="2.5.2"
# Atualize este sha256 quando bumpar a versão (sha256sum do tarball oficial).
UNITY_SHA256="0000000000000000000000000000000000000000000000000000000000000000"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DEST="$REPO_ROOT/tests/unity"
TARBALL="unity-$UNITY_VERSION.tar.gz"
URL="https://github.com/ThrowTheSwitch/Unity/archive/refs/tags/v$UNITY_VERSION.tar.gz"

mkdir -p "$DEST"

if [ -f "$DEST/unity.h" ] && [ -f "$DEST/Unity.c" ] && [ -f "$DEST/unity_internals.h" ]; then
  echo "Unity já instalado em $DEST — remova para reinstalar."
  exit 0
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"

echo "Baixando Unity v$UNITY_VERSION ..."
curl -fsSL -o "$TARBALL" "$URL"

# Verificação best-effort — se o sha256 não bater (ex.: bump de versão sem atualizar o hash),
# avisamos mas não bloqueamos, porque o usuário pode estar testando uma versão nova.
ACTUAL_SHA="$(sha256sum "$TARBALL" | awk '{print $1}')"
if [ "$ACTUAL_SHA" != "$UNITY_SHA256" ] && [ "$UNITY_SHA256" != "0000000000000000000000000000000000000000000000000000000000000000" ]; then
  echo "AVISO: sha256 não bate (esperado $UNITY_SHA256, obtido $ACTUAL_SHA)." >&2
  echo "  Se você confia no tarball, edite scripts/build-unity.sh e atualize o hash." >&2
  echo "  Continuando mesmo assim..." >&2
fi

tar xzf "$TARBALL"
SRC="Unity-$UNITY_VERSION/src"

cp "$SRC/unity.h" "$SRC/unity.c" "$SRC/unity_internals.h" "$DEST/"

echo "Unity v$UNITY_VERSION instalado em $DEST"
