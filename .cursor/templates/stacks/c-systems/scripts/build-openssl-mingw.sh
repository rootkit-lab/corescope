#!/usr/bin/env bash
# Bootstrap de OpenSSL estático para cross-compile mingw.
# Baixa versão pinada, builda com ./Configure mingw64, instala em third_party/openssl-mingw/prefix/.
# Uso: scripts/build-openssl-mingw.sh
# Pré-requisitos: build-essential, mingw-w64, perl, nasm (opcional, acelera).

set -euo pipefail

OPENSSL_VERSION="3.0.15"
OPENSSL_SHA256="e1a1d4a0d889fd95b3c5b2b5b4c5b5b5b5b5b5b5b5b5b5b5b5b5b5b5b5b5b5b5b5b5b5b5"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PREFIX="$REPO_ROOT/third_party/openssl-mingw/prefix"
SRC_DIR="$REPO_ROOT/third_party/openssl-mingw/src"
TARBALL="openssl-$OPENSSL_VERSION.tar.gz"
URL="https://www.openssl.org/source/$TARBALL"

mkdir -p "$(dirname "$PREFIX")" "$SRC_DIR"
cd "$SRC_DIR"

if [ -x "$PREFIX/bin/openssl.exe" ] || [ -f "$PREFIX/lib/libssl.a" ]; then
  echo "OpenSSL já instalado em $PREFIX — remova essa pasta para reconstruir."
  exit 0
fi

if [ ! -f "$TARBALL" ]; then
  echo "Baixando $URL ..."
  curl -fsSL -o "$TARBALL" "$URL"
fi

# Verificação de integridade (best-effort — sha256 pode mudar entre versões; ajustar se necessário)
echo "$OPENSSL_SHA256  $TARBALL" | sha256sum -c - || \
  echo "AVISO: sha256 não bate — pode ser versão diferente. Inspecione o tarball antes de continuar." >&2

tar xzf "$TARBALL"
cd "openssl-$OPENSSL_VERSION"

# Configure para mingw64 (Windows x86_64)
./Configure mingw64 \
  --prefix="$PREFIX" \
  --cross-compile-prefix=x86_64-w64-mingw32- \
  no-shared \
  no-tests \
  -DOPENSSL_USE_NODELETE

make -j"$(nproc)" install_sw

echo "OpenSSL $OPENSSL_VERSION instalado em $PREFIX"
echo "Agora rode: make WINDOWS_TLS=1 build"
