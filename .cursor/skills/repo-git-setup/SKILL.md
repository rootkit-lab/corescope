---
name: repo-git-setup
description: >-
  Inicializa o Git de um projeto novo gerado a partir do skink: histórico limpo
  (não herdado do template), hooks (.githooks), primeiro commit, e opcionalmente
  repositório remoto no GitHub com branch protection via gh CLI. Use durante o
  bootstrap (chamado por project-bootstrap) ou quando o usuário pedir para
  "configurar o git"/"criar o repositório no GitHub".
---

# Configuração de Git do projeto

## 1. Garantir histórico novo (não herdado do skink)

```bash
git rev-parse --is-inside-work-tree 2>/dev/null && git rev-parse --show-toplevel
```

- Se não houver `.git` nesta pasta: `git init` normalmente.
- Se já houver `.git` (por exemplo, porque o usuário clonou o skink via `git clone` em vez de copiar os arquivos): **confirme explicitamente com o usuário** antes de `rm -rf .git && git init` — isso apaga o histórico do template, que é o comportamento esperado, mas deve ser uma decisão consciente, não silenciosa.

```bash
git init -b main   # Git >= 2.28; em versões antigas: git init && git checkout -b main
```

Branch padrão: `main`.

## 2. Ativar os hooks versionados

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit .githooks/commit-msg
```

Confirme:

```bash
git config core.hooksPath   # deve imprimir ".githooks"
```

## 3. Ajustar `.gitignore` ao projeto real

O `.gitignore` do template já cobre segredos, artefatos de build genéricos e dependências das stacks mais comuns. Adicione linhas específicas do projeto se necessário (ex.: pasta de uploads, cache de build específico do framework escolhido) — sempre **complementando**, não substituindo, o que já existe.

## 4. Primeiro commit

```bash
git add -A
git commit -m "chore: bootstrap do projeto a partir do template skink"
```

Se o hook `commit-msg` rejeitar a mensagem, ajuste o texto para bater com Conventional Commits (ver `CONTRIBUTING.md`) — não use `--no-verify`.

## 5. Repositório remoto (opcional, só se o usuário confirmou que quer GitHub + CI/CD no bootstrap)

Pré-requisito: `gh auth status` autenticado.

```bash
gh repo create <owner>/<nome-do-projeto> --private --source=. --remote=origin
git push -u origin main
```

Use `--public` se o usuário confirmar que o repositório deve ser público.

### Branch protection em `main`

`gh api --field` não aceita objetos JSON aninhados (falha com "is not an object") — use `--input` com um arquivo/heredoc JSON:

```bash
cat > /tmp/branch-protection.json <<'EOF'
{
  "required_status_checks": { "strict": true, "contexts": ["CI"] },
  "enforce_admins": false,
  "required_pull_request_reviews": { "required_approving_review_count": 0 },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
gh api repos/<owner>/<nome-do-projeto>/branches/main/protection --method PUT --input /tmp/branch-protection.json
```

Ajuste `contexts` para o nome real do job de CI criado pela skill `deploy-setup` (geralmente `CI` ou o nome do workflow — **precisa já ter rodado ao menos uma vez** no repositório, senão a API aceita mas o nome pode não corresponder a nenhum check real). `required_approving_review_count: 0` permite merge solo — ainda exige PR, apenas não exige aprovação de terceiros (ver `CONTRIBUTING.md` sobre o motivo de usar PR mesmo sozinho).

Se `gh` não estiver disponível/autenticado, explique ao usuário os passos manuais equivalentes na interface do GitHub (Settings → Branches → Add rule) em vez de pular a etapa silenciosamente.

### Outras configurações recomendadas do repositório

```bash
gh repo edit <owner>/<nome-do-projeto> \
  --enable-squash-merge --enable-merge-commit=false --enable-rebase-merge=false \
  --delete-branch-on-merge
```

Squash-only + delete branch on merge mantém o histórico de `main` linear (um commit por PR) e evita acumular branches órfãs — consistente com o squash merge recomendado em `CONTRIBUTING.md`.

Se o projeto for, ele mesmo, pensado para ser reutilizado como ponto de partida de outros repositórios (não é o caso comum — normalmente só o `skink` em si tem esse papel), marque como template:

```bash
gh api repos/<owner>/<nome-do-projeto> --method PATCH --field is_template=true
```

### Chamadas de rede podem falhar de forma transitória

Comandos `gh api`/`git push`/`git fetch` contra o GitHub podem falhar por timeout de rede intermitente, não só por erro de configuração. Antes de assumir que um comando está preso ou mal configurado, tente de novo uma vez (idealmente com `timeout N <comando>` para não bloquear indefinidamente).

## Não fazer

- Não force-push nem sobrescreva histórico remoto existente sem confirmação explícita.
- Não crie o repositório remoto como público por padrão — confirme a visibilidade com o usuário.
- Não pule a ativação de `core.hooksPath` — sem ela, os hooks de `.githooks/` simplesmente não rodam e ninguém percebe.
