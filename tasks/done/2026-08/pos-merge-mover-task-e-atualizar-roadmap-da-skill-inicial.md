---
branch: "chore/pos-merge-mover-task-e-atualizar-roadmap-da-skill-inicial"
status: done
approved: true
pr: "https://github.com/rootkit-lab/corescope/pull/2"
created: "2026-08-13"
---

# pos-merge: mover task e atualizar roadmap da skill inicial

## Objetivo

Housekeeping pós-merge do PR #1 (skill inicial): mover a task concluída para `tasks/done/`,
corrigir a branch protection do `main` (contexto de status check errado estava bloqueando
merges) e corrigir um bug no script `new-task.sh` que corrompia `tasks/README.md`.

## Escopo

- [x] Corrigir branch protection do `main`: contexto exigido era `"CI / verify"`, mas o nome
      real do check reportado pelo GitHub Actions é `"verify"` — isso deixava todo PR travado
      em `BLOCKED` para sempre, mesmo com o CI verde
- [x] Mover `tasks/active/feat/skill-inicial-de-forense-e-engenharia-reversa.md` para
      `tasks/done/2026-08/`, status `done`
- [x] Corrigir `tasks/README.md` (o bug abaixo tinha corrompido as tabelas "Ativas"/"Concluídas")
- [x] Corrigir `new-task.sh`: `echo >> tasks/README.md` sempre jogava a linha no fim do arquivo
      (dentro/depois da tabela "Concluídas recentes"), nunca na tabela "Ativas" correta

## Fora de escopo

- Qualquer mudança de produto/feature (isto é só housekeeping de processo)

## Critério de "pronto"

- `tasks/README.md` reflete o estado real (só esta task em "Ativas")
- `gh pr view` não mostra mais `mergeStateStatus: BLOCKED` por causa da branch protection
- PR aberto, CI verde

## Log

- 2026-08-13: PR #1 mergeado; ao tentar `gh pr merge` antes deste, o merge já tinha funcionado,
  mas a branch protection com contexto errado (`"CI / verify"` em vez de `"verify"`) deixava o
  PR como `BLOCKED` — corrigido antes do merge real. Aproveitei esta task de housekeeping para
  também corrigir o bug do `new-task.sh` que corrompia `tasks/README.md` (percebido ao criar
  a própria branch desta task).
