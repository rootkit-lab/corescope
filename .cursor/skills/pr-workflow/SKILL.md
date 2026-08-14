---
name: pr-workflow
description: >-
  Cria/atualiza o Pull Request via gh CLI a partir da task ativa, comenta progresso,
  e acompanha/corrige o CI em loop até o PR ficar mergeável. Use depois de
  verify-before-push, quando o usuário pedir para "abrir PR"/"atualizar PR", ou para
  checar o estado do CI de um PR já aberto.
---

# PR + acompanhamento de CI

Combina três coisas que normalmente são feitas juntas: abrir/atualizar o PR, monitorar o CI, e corrigir o CI quando falha — até o PR estar pronto para merge.

## Pré-requisitos

```bash
gh auth status
git remote -v   # origin configurado
```

Base branch: `main` (ajustar se o projeto usar outra).

## 1. Criar ou atualizar o PR

```bash
.cursor/skills/pr-workflow/scripts/create-or-update-pr.sh tasks/active/<tipo>/<slug>.md
```

O script:
1. Valida que a branch atual não é `main`/`master`.
2. `git push -u origin HEAD`.
3. `gh pr create` (se não existir PR para a branch) ou `gh pr edit` (se já existir) — corpo gerado a partir do objetivo/escopo da task.
4. Atualiza o frontmatter `pr:` e `status: in-review` no arquivo da task.
5. Comenta no PR com timestamp (sempre — é o que permite acompanhar progresso em tasks longas).

Sem task associada (só a branch atual):

```bash
.cursor/skills/pr-workflow/scripts/create-or-update-pr.sh
```

Comentário manual de progresso:

```bash
gh pr comment --body "Backend pronto, falta UI"
```

## 2. Acompanhar o CI

```bash
.cursor/skills/pr-workflow/scripts/monitor-ci.sh --watch
```

- Lista os runs mais recentes da branch atual.
- Com `--watch`, aguarda o run em andamento terminar.
- Ao final, resume: `success`, `failure` (com job/step/últimas linhas do log) ou `cancelled`.

## 3. Se o CI falhar — loop de correção

```
investigar (monitor-ci.sh --logs) → reproduzir local (make verify) → fix mínimo → commit → push → monitor-ci.sh --watch
```

Repetir até ficar verde. Regras do fix:
- Escopo mínimo — só o necessário para o erro específico reportado.
- Não enfraquecer checks do CI "para passar".
- Não refatorar código não relacionado ao erro.
- Se a falha não vem das alterações desta branch, sincronizar com `main` primeiro (pode já ter sido corrigido lá).

## 4. PR pronto para merge

Confirme antes de considerar mergeável:
1. CI verde.
2. Comentários de review (se houver) resolvidos.
3. Branch atualizada com `main` se houver conflito potencial.

Merge (squash, mantendo histórico linear — ver `CONTRIBUTING.md`):

```bash
gh pr merge --squash --delete-branch
```

Depois do merge: mova a task de `tasks/active/` para `tasks/done/<ano>-<mes>/`, atualize `tasks/README.md` e `ROADMAP.md`.

## Não fazer

- Não ignore falha de CI silenciosamente nem re-rode o job sem entender a causa.
- Não use `--no-verify` no push como substituto de corrigir o problema real.
- Não faça merge sem pedido explícito do usuário (mesmo com CI verde) — confirme antes.
- Não force-push em `main`/`master`.
