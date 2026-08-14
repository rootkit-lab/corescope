# Contribuindo

Convenções de engenharia usadas por qualquer projeto gerado a partir deste template — válidas mesmo trabalhando sozinho.

## Configuração inicial (uma vez por clone do repositório)

Este repositório tem hooks de Git versionados em `.githooks/` (fora de `.git/hooks/`, que não é versionado pelo Git). Ative-os logo após clonar:

```bash
git config core.hooksPath .githooks
```

Sem isso, os hooks **não rodam** nesse clone, e nada bloqueia localmente o commit acidental de segredos/artefatos de build ou mensagens fora do padrão antes do push. Confirme que está ativo com:

```bash
git config core.hooksPath   # deve imprimir ".githooks"
```

## Fluxo de trabalho — GitHub Flow (obrigatório, inclusive solo)

Este projeto segue [GitHub Flow](https://docs.github.com/pt/get-started/using-github/github-flow): `main` é sempre estável e **protegida** — nenhum commit chega lá exceto via merge de Pull Request.

1. **Localmente**: `.githooks/pre-commit` bloqueia qualquer `git commit` feito diretamente nas branches `main`/`master` (a única exceção é um merge em andamento, detectado via `MERGE_HEAD`).
2. **No GitHub** (se aplicável — ver skill `repo-git-setup`): a branch `main` pode ter *branch protection* configurada — exige Pull Request antes de qualquer mudança chegar nela, sem `push` direto nem `force-push`.

Passo a passo (ver também a skill `branch-task`, que automatiza os passos 1-3):

1. Confira o `ROADMAP.md` antes de começar.
2. Atualize sua `main` local: `git checkout main && git pull --ff-only`.
3. Crie uma branch a partir de `main`:
   - `feat/<descrição-curta>` — nova funcionalidade
   - `fix/<descrição-curta>` — correção de bug
   - `chore/<descrição-curta>` — infraestrutura, configuração, tooling, documentação
   - `security/<descrição-curta>` — mudanças relacionadas a hardening/segurança
   - `docs/<descrição-curta>` — documentação pura (sem mudança de código/infra)
   - `refactor/<descrição-curta>` / `test/<descrição-curta>` — refatoração / testes
4. Faça commits pequenos e coerentes nessa branch (ver convenção de commits abaixo).
5. Atualize o `ROADMAP.md` marcando os checkboxes concluídos **na mesma branch/PR**, não depois.
6. Se a mudança alterar uma decisão de arquitetura documentada no `PLAN.md`, atualize o `PLAN.md` também, na mesma branch.
7. Rode `make verify` (skill `verify-before-push`) antes de dar push.
8. Envie a branch e abra um Pull Request (skill `pr-workflow`, ou `gh pr create`/interface do GitHub) — mesmo trabalhando sozinho.
9. Acompanhe o CI até ficar verde (skill `pr-workflow` cobre isso) e faça o merge via **squash merge** — mantém a `main` com histórico linear, um commit por PR.
10. Sincronize sua `main` local (`git checkout main && git pull --ff-only`) e remova a branch local.

### Por que PR mesmo trabalhando sozinho?

O PR é o checkpoint onde você olha o diff inteiro de uma vez (não arquivo por arquivo enquanto edita), o que pega erros como uma porta exposta por engano, um `console.log` esquecido, ou um arquivo que não deveria estar ali.

## Convenção de commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/), validado pelo hook `.githooks/commit-msg`:

```
<tipo>(<escopo opcional>): <descrição curta no imperativo>

[corpo opcional explicando o porquê]
```

Tipos usados: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `security`, `perf`.

Exemplos:

```
feat(api): adiciona endpoint de listagem de usuários
fix(auth): corrige expiração de token
chore(ci): adiciona workflow de release
docs(plan): atualiza decisão de banco de dados
```

## Antes de abrir PR / finalizar uma tarefa

- [ ] `make verify` limpo (format/lint/vet/build/test — o que o preset de stack define)
- [ ] Nenhum segredo (chave privada, token, senha) commitado — confira `git diff` antes do commit (o hook `.githooks/pre-commit` bloqueia os casos mais óbvios, mas não é infalível)
- [ ] Nenhum artefato de build (binário, `dist/`, instalador) commitado
- [ ] Checkboxes relevantes do `ROADMAP.md` atualizados
- [ ] Se a mudança tocou infraestrutura/segurança: rodar a skill `security-baseline-audit`

## Testando localmente

Ver skill `dev-environment-setup` para como rodar o projeto localmente e a skill `verify-before-push` para os gates equivalentes ao CI.

## Convenção de código

- Comentários e documentação: português (ou o idioma escolhido na entrevista de bootstrap).
- Identificadores (variáveis, funções, tipos): inglês, seguindo o idiomático da stack escolhida.
- Ver `.cursor/rules/*.mdc` para convenções específicas de cada parte do código — geradas a partir do preset de stack escolhido no bootstrap.
