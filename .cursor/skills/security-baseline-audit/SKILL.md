---
name: security-baseline-audit
description: >-
  Roda uma auditoria read-only de segurança do projeto e (se aplicável) do
  servidor de produção: segredos no repositório, dependências vulneráveis,
  configuração de SSH/firewall/portas expostas. Use antes/depois de mudanças de
  infraestrutura, firewall ou rede, periodicamente conforme o ROADMAP.md, ou quando
  o usuário pedir para "checar a segurança".
---

# Auditoria de segurança (baseline)

Todos os checks são **read-only** — esta skill nunca altera configuração, só relata o que encontrou. Correções são uma decisão separada e explícita do usuário.

## Uso

```bash
# Checks locais (repositório): segredos, dependências vulneráveis
.cursor/skills/security-baseline-audit/scripts/audit.sh local

# Checks no servidor de produção (só se o deploy for VPS próprio — ver PLAN.md)
.cursor/skills/security-baseline-audit/scripts/audit.sh vps <usuario@host>
```

## O que o modo `local` verifica

1. Segredos versionados por engano: `git log --all` + working tree, padrões de chave privada/token de API (mesma lógica do hook `pre-commit`, mas olhando o histórico inteiro, não só o que está em staging).
2. Arquivos de segredo (`.env`, `*.key`, `*.pem`) presentes no working tree mas fora do `.gitignore`.
3. Dependências com vulnerabilidades conhecidas, usando a ferramenta disponível para a stack do projeto (`govulncheck`, `npm audit`, `pip-audit` — o script detecta pelo que existe no projeto/PATH).

## O que o modo `vps` verifica (via SSH, read-only)

1. Configuração efetiva do SSH (`sshd -T`) — `passwordauthentication`, `permitrootlogin`, `kbdinteractiveauthentication`.
2. Status do `ufw`/firewall — deve estar ativo, com regras restritas ao que está registrado em `PLAN.md` (seção de alocação de portas, se o projeto tiver uma).
3. `net.ipv4.ip_forward` — só deve ser `1` se o projeto precisa rotear tráfego (ex.: VPN, proxy); confira contra a decisão documentada em `PLAN.md`.
4. Todas as portas TCP/UDP escutando (`ss -tulnp`) — compare manualmente com o que está documentado em `PLAN.md`; qualquer porta não documentada é uma bandeira vermelha.
5. Serviços que deveriam estar restritos a uma rede interna/VPN (bancos de dados, painéis internos) — confirmar que não estão vinculados a `0.0.0.0` nem à interface pública.

## Como interpretar o resultado

Depois de rodar, confira item a item contra o que `PLAN.md`/`SECURITY.md` do projeto dizem que *deveria* ser verdade — não assuma que "rodou sem erro" significa "está seguro". Se algum item falhar:

1. Reporte ao usuário explicitamente qual invariante de `SECURITY.md` foi violada.
2. Não corrija automaticamente sem confirmação — mudanças de firewall/rede em produção podem cortar o próprio acesso.
3. Depois da correção (feita com o usuário), rode a auditoria de novo para confirmar.

## Não fazer

- Não rode comandos que alterem firewall/rede/serviços a partir desta skill — ela é só diagnóstico. Mudanças reais passam pelo fluxo normal (branch-task → verify → PR), com um passo read-only antes e depois.
- Não ignore um achado "porque provavelmente não é nada" — registre e pergunte.
