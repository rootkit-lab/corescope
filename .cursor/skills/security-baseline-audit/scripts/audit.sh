#!/usr/bin/env bash
# Auditoria de segurança read-only, genérica.
# Uso:
#   audit.sh local
#   audit.sh vps <usuario@host>
set -uo pipefail

mode="${1:-}"

section() { printf '\n== %s ==\n' "$1"; }

audit_local() {
  section "Segredos no histórico e no working tree"
  pattern='-----BEGIN( RSA| OPENSSH| EC| DSA)? PRIVATE KEY-----|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|xox[baprs]-[0-9A-Za-z-]{10,}'
  if git log --all -p 2>/dev/null | grep -E "$pattern" >/dev/null 2>&1; then
    echo "[ATENÇÃO] padrão de segredo encontrado no histórico do git (git log -p)."
  else
    echo "[OK] nenhum padrão óbvio de segredo no histórico."
  fi

  echo ""
  echo "Arquivos de segredo no working tree (verificar se estão no .gitignore):"
  find . -maxdepth 4 -type f \( -name '.env' -o -name '.env.*' -o -name '*.key' -o -name '*.pem' -o -name '*credentials*.json' \) \
    -not -name '*.example' -not -path './node_modules/*' -not -path './.git/*' 2>/dev/null | while read -r f; do
    if git check-ignore -q "$f"; then
      echo "  [OK, ignorado] $f"
    else
      echo "  [ATENÇÃO, NÃO ignorado] $f"
    fi
  done

  section "Dependências vulneráveis"
  if command -v govulncheck >/dev/null 2>&1 && [[ -f go.mod ]]; then
    govulncheck ./... || true
  elif [[ -f package.json ]] && command -v npm >/dev/null 2>&1; then
    npm audit --omit=dev || true
  elif command -v pip-audit >/dev/null 2>&1 && { [[ -f requirements.txt ]] || [[ -f pyproject.toml ]]; }; then
    pip-audit || true
  else
    echo "Nenhuma ferramenta de audit de dependências detectada para a stack deste projeto (ok se ainda não há dependências)."
  fi
}

audit_vps() {
  local target="${1:?uso: audit.sh vps <usuario@host>}"
  # ConnectTimeout evita travar indefinidamente se o host estiver inacessível.
  local ssh_opts=(-o ConnectTimeout=10 -o BatchMode=yes)

  section "SSH (sshd -T)"
  ssh "${ssh_opts[@]}" "$target" 'sshd -T 2>/dev/null | grep -iE "passwordauthentication|permitrootlogin|kbdinteractiveauthentication"' || echo "[ERRO] não foi possível checar sshd -T (permissão/timeout?)"

  section "Firewall (ufw)"
  ssh "${ssh_opts[@]}" "$target" 'command -v ufw >/dev/null 2>&1 && ufw status verbose || echo "ufw não instalado"'

  section "IP forwarding"
  ssh "${ssh_opts[@]}" "$target" 'sysctl net.ipv4.ip_forward 2>/dev/null'

  section "Portas escutando (ss -tulnp)"
  ssh "${ssh_opts[@]}" "$target" 'ss -tulnp 2>/dev/null || netstat -tulnp 2>/dev/null'

  echo ""
  echo "Compare a saída acima com a tabela de alocação de portas/domínios em PLAN.md."
}

case "$mode" in
  local)
    audit_local
    ;;
  vps)
    audit_vps "${2:-}"
    ;;
  *)
    echo "Uso: $0 local | $0 vps <usuario@host>" >&2
    exit 1
    ;;
esac
