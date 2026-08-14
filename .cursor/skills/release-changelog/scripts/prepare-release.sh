#!/usr/bin/env bash
# Prepara e publica uma release: valida CHANGELOG, cria tag semver, push.
# Uso: prepare-release.sh --version X.Y.Z [--dry-run]
set -euo pipefail

version=""
dry_run=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) version="$2"; shift 2 ;;
    --dry-run) dry_run=true; shift ;;
    *) shift ;;
  esac
done

if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "ERRO: --version deve estar no formato X.Y.Z (recebido: '$version')" >&2
  exit 1
fi

changelog="CHANGELOG.md"
[[ -f "$changelog" ]] || { echo "ERRO: $changelog não encontrado." >&2; exit 1; }

unreleased_body="$(awk '/^## \[Unreleased\]/{flag=1;next}/^## \[/{flag=0}flag' "$changelog" | sed '/^\s*$/d')"
if [[ -z "$unreleased_body" ]]; then
  echo "ERRO: seção [Unreleased] do $changelog está vazia. Preencha antes de liberar uma release." >&2
  exit 1
fi

if ! $dry_run; then
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERRO: working tree com alterações não commitadas. Commit/stash antes de continuar." >&2
    exit 1
  fi
fi

tag="v$version"
if git rev-parse "$tag" >/dev/null 2>&1; then
  echo "ERRO: tag $tag já existe." >&2
  exit 1
fi

today="$(date +%Y-%m-%d)"
full_unreleased="$(awk '/^## \[Unreleased\]/{flag=1;print;next}/^## \[/{flag=0}flag' "$changelog")"

if $dry_run; then
  echo "--- Preview do que entraria em [$version] - $today ---"
  echo "$full_unreleased" | tail -n +2
  echo "--- fim do preview (nada foi alterado, --dry-run) ---"
  exit 0
fi

python3 - "$changelog" "$version" "$today" <<'PYEOF'
import re, sys

path, version, today = sys.argv[1:4]
with open(path, encoding="utf-8") as f:
    content = f.read()

pattern = re.compile(r"(## \[Unreleased\]\n)(.*?)(?=\n## \[|\Z)", re.DOTALL)
m = pattern.search(content)
if not m:
    sys.exit("Não encontrei a seção [Unreleased] para processar.")

body = m.group(2).rstrip("\n")
new_section = f"## [Unreleased]\n\n## [{version}] - {today}\n{body}\n"
content = content[:m.start()] + new_section + content[m.end():]

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
PYEOF

git add "$changelog"
git commit -m "chore(release): v$version"
git tag -a "$tag" -m "Release $tag"

tcmd=(); command -v timeout >/dev/null 2>&1 && tcmd=(timeout 60)

echo "Tag $tag criada. Publicando..."
"${tcmd[@]}" git push origin HEAD
"${tcmd[@]}" git push origin "$tag"

echo "Release $tag publicada. Acompanhe com:"
echo "  .cursor/skills/pr-workflow/scripts/monitor-ci.sh --workflow Release --watch"
