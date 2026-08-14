#!/usr/bin/env bash
# beforeShellExecution hook: bloqueia padrões de comando claramente destrutivos ou
# que contornem os gates de segurança do repositório (genérico, não depende de stack).
set -uo pipefail

input="$(cat)"

deny() {
  local reason="$1"
  local user_msg="guard-shell bloqueou o comando: $reason"
  local agent_msg="Comando bloqueado por padrão destrutivo/perigoso ($reason). Explique ao usuário e peça confirmação explícita antes de tentar de outra forma."
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import json, sys; print(json.dumps({"permission": "deny", "userMessage": sys.argv[1], "agentMessage": sys.argv[2]}))' "$user_msg" "$agent_msg"
  else
    printf '{"permission":"deny","userMessage":"%s","agentMessage":"%s"}\n' "$user_msg" "$agent_msg"
  fi
  exit 2
}

# Cada entrada: descrição | regex estendida (case-insensitive) aplicada ao payload bruto do hook
declare -a checks=(
  "rm -rf em raiz/home|rm[[:space:]]+(-[a-zA-Z]*[rf][a-zA-Z]*){1,}[[:space:]]+(/|~)([[:space:]]|$)"
  "fork bomb|:\(\)[[:space:]]*\{[[:space:]]*:\|:&[[:space:]]*\};:"
  "mkfs em dispositivo|mkfs\.[a-z0-9]+[[:space:]]+/dev/"
  "dd para disco bruto|dd[[:space:]].*of=/dev/(sd|nvme|hd|vd)[a-z]*([[:space:]]|$)"
  "force-push em main/master|git[[:space:]]+push[[:space:]].*(--force|-f[[:space:]]).*(main|master)"
  "force-push em main/master (ordem inversa)|git[[:space:]]+push[[:space:]].*(main|master).*(--force|[[:space:]]-f([[:space:]]|$))"
  "reset --hard contra origin/main|git[[:space:]]+reset[[:space:]]+--hard[[:space:]]+origin/(main|master)"
  "bypass de hooks sem confirmação|--no-verify"
  "chmod 777 recursivo em raiz|chmod[[:space:]]+-R[[:space:]]+777[[:space:]]+/([[:space:]]|$)"
  "DROP DATABASE|DROP[[:space:]]+DATABASE"
  "TRUNCATE TABLE em produção|TRUNCATE[[:space:]]+TABLE"
  "desativar firewall|ufw[[:space:]]+disable"
  "flush de firewall|iptables[[:space:]]+-F([[:space:]]|$)"
  "redirecionar para dispositivo de disco|>[[:space:]]*/dev/(sd|nvme|hd|vd)[a-z]"
)

for entry in "${checks[@]}"; do
  desc="${entry%%|*}"
  pattern="${entry#*|}"
  if printf '%s' "$input" | grep -qEi -e "$pattern"; then
    deny "$desc"
  fi
done

exit 0
