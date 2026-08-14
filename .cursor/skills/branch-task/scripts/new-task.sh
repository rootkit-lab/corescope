#!/usr/bin/env bash
# Cria uma branch + arquivo de task antes de codar.
# Uso: new-task.sh <feat|fix|chore|docs|refactor|test|security> "<título curto>"
set -euo pipefail

skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

type="${1:-}"
title="${2:-}"

valid_types="feat fix chore docs refactor test security"
if [[ -z "$type" || -z "$title" ]]; then
  echo "Uso: $0 <tipo> \"<título curto>\"" >&2
  echo "Tipos válidos: $valid_types" >&2
  exit 1
fi
if ! grep -qw "$type" <<<"$valid_types"; then
  echo "Tipo inválido: '$type'. Use um de: $valid_types" >&2
  exit 1
fi

slug="$(echo "$title" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')"
branch="$type/$slug"

current_branch="$(git branch --show-current 2>/dev/null || echo "")"
if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
  if git remote get-url origin >/dev/null 2>&1; then
    # timeout evita travar indefinidamente se a rede estiver lenta/instável —
    # seguir com o estado local em vez de bloquear a criação da branch.
    if command -v timeout >/dev/null 2>&1; then
      timeout 15 git fetch origin "$current_branch" --quiet \
        && timeout 15 git pull --ff-only --quiet \
        || echo "Aviso: não foi possível atualizar $current_branch via rede (timeout/erro) — seguindo com o estado local."
    else
      git fetch origin "$current_branch" --quiet && git pull --ff-only --quiet \
        || echo "Aviso: não foi possível atualizar $current_branch (seguindo mesmo assim)."
    fi
  fi
fi

if git show-ref --verify --quiet "refs/heads/$branch"; then
  echo "Branch '$branch' já existe — trocando para ela em vez de recriar."
  git checkout "$branch"
else
  git checkout -b "$branch"
fi

mkdir -p tasks/_templates tasks/active/"$type"

if [[ ! -f tasks/_templates/TASK.md ]]; then
  cp "$skill_dir/assets/TASK.template.md" tasks/_templates/TASK.md
fi

if [[ ! -f tasks/README.md ]]; then
  cat > tasks/README.md <<'EOF'
# Tasks

Índice de tasks ativas e concluídas. Cada task vive em `tasks/active/<tipo>/<slug>.md`
enquanto está em andamento, e é movida para `tasks/done/<ano>-<mes>/` após o merge.

## Ativas

| Task | Branch | Status |
|---|---|---|
EOF
fi

task_file="tasks/active/$type/$slug.md"
today="$(date +%Y-%m-%d)"

if [[ -f "$task_file" ]]; then
  echo "Task já existe em $task_file — não sobrescrevendo."
else
  # python3 em vez de sed: $branch contém "/", o que quebraria o delimitador do sed.
  python3 -c '
import sys
tpl, branch, title, date, out = sys.argv[1:6]
with open(tpl, encoding="utf-8") as f:
    content = f.read()
content = content.replace("{{BRANCH}}", branch).replace("{{TITLE}}", title).replace("{{DATE}}", date)
with open(out, "w", encoding="utf-8") as f:
    f.write(content)
' tasks/_templates/TASK.md "$branch" "$title" "$today" "$task_file"
  # Insere a linha na tabela "## Ativas" (não no fim do arquivo — que cairia dentro/depois
  # da tabela "## Concluídas recentes" e corromperia as duas tabelas).
  python3 -c '
import sys

path, title, branch = sys.argv[1:4]
with open(path, encoding="utf-8") as f:
    lines = f.readlines()

insert_at = len(lines)
for i, line in enumerate(lines):
    if line.strip() == "## Ativas":
        for j in range(i + 1, len(lines)):
            if lines[j].startswith("|---"):
                insert_at = j + 1
                break
        break

lines.insert(insert_at, f"| {title} | `{branch}` | todo |\n")
with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)
' tasks/README.md "$title" "$branch"
  echo "Task criada em $task_file"
fi

echo "Branch atual: $branch"
