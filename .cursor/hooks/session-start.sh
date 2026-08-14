#!/usr/bin/env bash
# sessionStart hook: injeta lembrete do estado de bootstrap no início de cada conversa.
# sessionStart é fire-and-forget (não bloqueia) — isto é só um reforço de contexto,
# a garantia real vem de AGENTS.md + .cursor/rules/000-bootstrap.mdc.
set -uo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
state_file="$repo_root/.cursor/state/bootstrap.json"

status="pending"
if [[ -f "$state_file" ]] && command -v python3 >/dev/null 2>&1; then
  status="$(python3 -c '
import json, sys
try:
    with open(sys.argv[1]) as f:
        data = json.load(f)
    print(data.get("status", "pending"))
except Exception:
    print("pending")
' "$state_file" 2>/dev/null || echo pending)"
fi

if [[ "$status" == "pending" ]]; then
  context='LEMBRETE DE SISTEMA: .cursor/state/bootstrap.json esta com status pending (nao done) - este repositorio ainda e o template skink, sem projeto real definido. Sua PRIMEIRA resposta nesta conversa deve ser a entrevista de bootstrap (nome do projeto, tipo, stack, onde roda em producao, escala, seguranca) descrita em .cursor/skills/project-bootstrap/SKILL.md. Nao edite codigo nem crie arquivos de projeto antes de concluir essa entrevista.'
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import json, sys; print(json.dumps({"additional_context": sys.argv[1]}))' "$context"
  else
    printf '{"additional_context": "%s"}\n' "$context"
  fi
fi

exit 0
