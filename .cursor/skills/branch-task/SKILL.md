---
name: branch-task
description: >-
  Planeja o trabalho antes de codar: cria uma branch e um arquivo de task em
  tasks/active/ com objetivo, escopo, checklist e log — nunca trabalha direto em
  main/master. Use sempre que o usuário pedir uma nova feature/fix/chore, antes de
  escrever qualquer código, ou quando ele disser "cria uma task"/"nova branch".
---

# Planejar branch + task antes de codar

Regra absoluta: **nenhum código sem branch, nenhuma branch sem task.** Isso é o que torna o PR (skill `pr-workflow`) revisável e o `ROADMAP.md` confiável.

## Fluxo

1. **Verificar branch atual:**

```bash
git branch --show-current
```

Se for `main`/`master`, pare — não trabalhe aqui. Continue para o passo 2.

2. **Evitar duplicar trabalho:** olhe `tasks/active/` (e `tasks/README.md`, se existir) — se já há uma task incompleta para o mesmo objetivo, continue-a em vez de criar outra.

3. **Criar branch + task:**

```bash
.cursor/skills/branch-task/scripts/new-task.sh <tipo> "<título curto>"
# ex.: .cursor/skills/branch-task/scripts/new-task.sh feat "listagem de usuários paginada"
```

Tipos válidos: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `security`.

O script:
- Garante que `main` local está atualizada antes de ramificar (`git fetch && git checkout main && git pull --ff-only`, se houver remoto configurado).
- Cria a branch `<tipo>/<slug>`.
- Copia `tasks/_templates/TASK.md` para `tasks/active/<tipo>/<slug>.md`.
- Atualiza `tasks/README.md` com a nova task na tabela de "ativas".

4. **Preencher a task** (`tasks/active/<tipo>/<slug>.md`): objetivo, escopo (lista do que entra/não entra), critério de "pronto". Deixe a seção de log vazia — ela é preenchida durante o trabalho.

5. **Implementar**, marcando itens do escopo como `[x]` conforme entrega, e adicionando uma linha no log a cada sessão de trabalho relevante ou erro encontrado:

```markdown
## Log
- 2026-08-12: implementado endpoint GET /users, faltam testes
- 2026-08-12: corrigido bug de paginação (offset invertido)
```

6. **Antes de abrir PR:** skill `verify-before-push`, depois `pr-workflow`.

## Estrutura

```
tasks/
├── README.md              # tabela de tasks ativas + histórico recente
├── _templates/TASK.md      # modelo usado pelo new-task.sh
└── active/
    └── <tipo>/<slug>.md
```

Depois do merge (ver skill `pr-workflow`), mova a task para `tasks/done/<ano>-<mes>/` — não delete, é histórico útil.

## Não fazer

- Não implemente código com uma task marcada como "só planejar"/bloqueada por decisão pendente do usuário.
- Não crie a task depois do código já escrito — a ordem importa, é o que torna o PR revisável.
- Não trabalhe em `main`/`master` mesmo "só para testar rápido".
