---
name: verify-before-push
description: >-
  Roda o gate local (make verify) antes de qualquer git push, espelhando o que o CI
  vai checar. Use sempre antes de dar push, antes de abrir/atualizar um PR, ou
  quando o usuário pedir para "validar o repositório".
---

# Verificar antes do push

## Comando

```bash
make install   # se ainda não instalou dependências / lockfile mudou
make verify
```

`make verify` é o contrato definido pela skill `dev-environment-setup` (implementado no `Makefile` gerado a partir do preset de stack) e deve rodar exatamente o que o job `verify` do CI roda (ver skill `deploy-setup` / `.github/workflows/ci.yml`) — se os dois divergem, "passou local" não significa nada.

Tipicamente cobre: formatação, lint/vet, build, testes.

## Se falhar

1. Leia a saída — não tente "consertar" ignorando o erro (ex.: desabilitar um lint rule só para passar).
2. Corrija o mínimo necessário para o erro específico.
3. Rode `make verify` de novo até ficar limpo.

## Commit message

Formato exigido pelo hook `.githooks/commit-msg` (Conventional Commits — ver `CONTRIBUTING.md`):

```
feat(escopo): descrição curta
fix(escopo): corrige X
docs: atualiza README
```

## Push

```bash
git push -u origin <branch>
```

Se `pre-commit`/`commit-msg` falharem, corrija e comite de novo — **não use `--no-verify`** salvo confirmação explícita do usuário para um caso excepcional.

## Depois do push

Siga para a skill `pr-workflow` (criar/atualizar PR e acompanhar o CI até ficar mergeável).

## Não fazer

- Não dê push com `make verify` falhando "para ver se o CI também falha" — isso desperdiça tempo de CI e histórico de commits com correções triviais.
- Não enfraqueça checks do CI/`make verify` só para conseguir passar — se um check está genuinamente errado, discuta com o usuário antes de alterá-lo.
