#!/usr/bin/env bash
# Cria ou atualiza o PR da branch atual via gh CLI, opcionalmente a partir de uma task.
# Uso: create-or-update-pr.sh [tasks/active/<tipo>/<slug>.md] [--draft] [--no-push] [--comment "texto"]
set -euo pipefail

task_file=""
draft=false
do_push=true
extra_comment=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --draft) draft=true; shift ;;
    --no-push) do_push=false; shift ;;
    --comment) extra_comment="$2"; shift 2 ;;
    *.md) task_file="$1"; shift ;;
    *) shift ;;
  esac
done

branch="$(git branch --show-current)"
if [[ "$branch" == "main" || "$branch" == "master" ]]; then
  echo "ERRO: não é possível abrir PR a partir de main/master." >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "ERRO: gh CLI não encontrado. Instale https://cli.github.com/ ou abra o PR manualmente." >&2
  exit 1
fi
gh auth status >/dev/null 2>&1 || { echo "ERRO: gh não autenticado (gh auth login)." >&2; exit 1; }

title="$branch"
body="Branch: \`$branch\`"

if [[ -n "$task_file" && -f "$task_file" ]]; then
  title="$(grep -m1 -E '^# ' "$task_file" | sed 's/^# //')"
  [[ -z "$title" ]] && title="$branch"
  objetivo="$(awk '/^## Objetivo/{flag=1;next}/^## /{flag=0}flag' "$task_file" | sed '/^$/d')"
  escopo="$(awk '/^## Escopo/{flag=1;next}/^## /{flag=0}flag' "$task_file")"
  body=$(cat <<EOF
## Objetivo
$objetivo

## Escopo
$escopo

## Test plan
- [ ] \`make verify\` local
- [ ] CI verde

_Task: \`$task_file\`_
EOF
)
fi

# timeout evita travar indefinidamente se a rede/GitHub estiver lento — falha
# explicitamente em vez de ficar preso sem feedback.
tcmd=(); command -v timeout >/dev/null 2>&1 && tcmd=(timeout 60)

if $do_push; then
  "${tcmd[@]}" git push -u origin HEAD
fi

pr_number="$(gh pr view --json number --jq .number 2>/dev/null || true)"

if [[ -n "$pr_number" ]]; then
  echo "PR #$pr_number já existe — atualizando."
  gh pr edit "$pr_number" --title "$title" --body "$body"
else
  create_args=(--title "$title" --body "$body" --base main)
  $draft && create_args+=(--draft)
  gh pr create "${create_args[@]}"
  pr_number="$(gh pr view --json number --jq .number 2>/dev/null || true)"
fi

timestamp="$(date -Iseconds)"
comment_body="Progresso em $timestamp"
[[ -n "$extra_comment" ]] && comment_body="$comment_body: $extra_comment"
gh pr comment --body "$comment_body" || true

if [[ -n "$task_file" && -f "$task_file" ]]; then
  pr_url="$(gh pr view --json url --jq .url 2>/dev/null || echo "")"
  sed -i.bak -E "s#^pr: .*#pr: \"$pr_url\"#; s#^status: .*#status: in-review#" "$task_file" && rm -f "$task_file.bak"
  echo "Task atualizada: $task_file (pr: $pr_url, status: in-review)"
fi

echo "PR: $(gh pr view --json url --jq .url 2>/dev/null || echo '(ver gh pr view)')"
