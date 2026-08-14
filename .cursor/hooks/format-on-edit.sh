#!/usr/bin/env bash
# afterFileEdit hook: formata o arquivo editado conforme a extensão, se a
# ferramenta correspondente estiver instalada (best-effort, nunca bloqueia).
set -uo pipefail

input="$(cat)"

file_path=""
if command -v python3 >/dev/null 2>&1; then
  file_path="$(printf '%s' "$input" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
for key in ("file_path", "filePath", "path"):
    v = data.get(key)
    if isinstance(v, str) and v:
        print(v)
        break
' 2>/dev/null || true)"
fi

if [[ -z "$file_path" ]]; then
  file_path="$(printf '%s' "$input" | grep -oE '"(file_path|filePath|path)"[[:space:]]*:[[:space:]]*"[^"]+"' | head -n1 | sed -E 's/.*:[[:space:]]*"([^"]+)"/\1/' || true)"
fi

if [[ -z "$file_path" || ! -f "$file_path" ]]; then
  exit 0
fi

case "$file_path" in
  *.go)
    if command -v goimports >/dev/null 2>&1; then
      goimports -w "$file_path" 2>/dev/null || true
    elif command -v gofmt >/dev/null 2>&1; then
      gofmt -w "$file_path" 2>/dev/null || true
    fi
    ;;
  *.ts|*.tsx|*.js|*.jsx|*.json|*.css|*.scss|*.md|*.yml|*.yaml)
    if [[ -x "./node_modules/.bin/prettier" ]]; then
      ./node_modules/.bin/prettier --write "$file_path" >/dev/null 2>&1 || true
    elif command -v prettier >/dev/null 2>&1; then
      prettier --write "$file_path" >/dev/null 2>&1 || true
    fi
    ;;
  *.py)
    if command -v ruff >/dev/null 2>&1; then
      ruff format "$file_path" >/dev/null 2>&1 || true
    elif command -v black >/dev/null 2>&1; then
      black -q "$file_path" >/dev/null 2>&1 || true
    fi
    ;;
  *.rs)
    command -v rustfmt >/dev/null 2>&1 && rustfmt "$file_path" >/dev/null 2>&1 || true
    ;;
esac

exit 0
