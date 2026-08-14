#!/usr/bin/env bash
# Monitora os runs de CI da branch atual via gh CLI.
# Uso: monitor-ci.sh [--watch] [--logs] [--run RUN_ID] [--workflow NOME] [--branch NOME]
set -euo pipefail

watch=false
show_logs=false
run_id=""
workflow="CI"
branch="$(git branch --show-current 2>/dev/null || echo "")"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --watch) watch=true; shift ;;
    --logs) show_logs=true; shift ;;
    --run) run_id="$2"; shift 2 ;;
    --workflow) workflow="$2"; shift 2 ;;
    --branch) branch="$2"; shift 2 ;;
    *) shift ;;
  esac
done

command -v gh >/dev/null 2>&1 || { echo "ERRO: gh CLI não encontrado." >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "ERRO: gh não autenticado." >&2; exit 1; }

if [[ -z "$run_id" ]]; then
  echo "Runs recentes (workflow=$workflow branch=$branch):"
  gh run list --workflow "$workflow" --branch "$branch" --limit 5 || gh run list --branch "$branch" --limit 5
  run_id="$(gh run list --branch "$branch" --limit 1 --json databaseId --jq '.[0].databaseId' 2>/dev/null || true)"
fi

if [[ -z "$run_id" ]]; then
  echo "Nenhum run encontrado para branch '$branch'."
  exit 0
fi

if $watch; then
  echo "Acompanhando run $run_id até concluir..."
  gh run watch "$run_id" --exit-status || true
fi

status="$(gh run view "$run_id" --json conclusion --jq .conclusion 2>/dev/null || echo "unknown")"
echo "Conclusão do run $run_id: ${status:-em andamento}"

if [[ "$status" == "failure" || "$show_logs" == true ]]; then
  echo ""
  echo "Logs das etapas com falha:"
  gh run view "$run_id" --log-failed || true
fi
