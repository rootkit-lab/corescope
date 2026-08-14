# Instruções para agentes de IA — corescope

Este arquivo contém o contexto que qualquer agente (Cursor, ou outro compatível com o padrão AGENTS.md) precisa ter sempre em mente ao trabalhar neste repositório.

## O que é este repositório

`corescope` é uma **Agent Skill (Cursor/Claude) + toolkit em Python 3** para forense de memória, análise estática de binários e engenharia reversa. Foi gerado a partir do template [`skink`](https://github.com/rootkit-lab/skink) — o bootstrap inicial já foi concluído (`.cursor/state/bootstrap.json` está `"done"`); as informações reais do projeto estão em `PLAN.md` (arquitetura/decisões) e `ROADMAP.md` (progresso por fase).

Se o usuário pedir explicitamente para refazer o bootstrap do zero (raro — normalmente só faz sentido no `skink` original, não aqui), use o comando `/start-project` e **confirme antes de sobrescrever** `PLAN.md`/`ROADMAP.md`/`SECURITY.md` já preenchidos.

## Regra central do domínio: nunca "responder de memória"

Este projeto existe justamente para substituir respostas de IA por memória/treino por **verificação empírica**: antes de afirmar algo sobre uma amostra (binário, memory dump), rode a ferramenta (Volatility3, `pyelftools`/`LIEF`, `capstone`, `yara-python`, `angr`/`unicorn`, ou CLI externa como `radare2`/`objdump`/`strings`) e cite o comando/endereço/offset que sustenta a afirmação. Ver `skill/corescope/SKILL.md` para a tabela de precedência de fontes.

## Guardrail ético e legal (aplica-se a qualquer tarefa neste repo)

- Só ajude a analisar amostras/sistemas que o usuário possui ou está expressamente autorizado a examinar (laboratório próprio, CTF, engajamento de IR autorizado, pesquisa acadêmica).
- Nunca ajude a produzir malware funcional para uso não autorizado, nem a automatizar ataque/exploração contra sistema sem autorização explícita do proprietário.
- Qualquer análise dinâmica de binário não confiável deve acontecer isolada (`Dockerfile` sandbox, `--network=none`) — nunca sugira rodar a amostra direto no host.
- Nunca commite amostras de malware reais, memory dumps de terceiros, ou dados de caso/cliente — ver `.gitignore` e `SECURITY.md`.

## Convenções gerais (herdadas do template `skink`, valem para todo o projeto)

- Documentação e comunicação com o usuário: **português (pt-BR)**. Identificadores de código (variáveis, funções, nomes de pacotes): **inglês**. Conteúdo da skill (`skill/corescope/`) também em **inglês** — é o padrão já usado nas outras skills pessoais do autor e maximiza a utilidade se a skill for reaproveitada fora deste repositório.
- Fluxo de Git: **GitHub Flow obrigatório, inclusive solo** — nenhum commit direto em `main`, toda mudança nasce numa branch e chega via Pull Request. Ver [`CONTRIBUTING.md`](./CONTRIBUTING.md).
- Commits: **Conventional Commits** (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `security`, `perf`), aplicado por `.githooks/commit-msg`.
- Nunca commitar segredos nem artefatos de build — `.gitignore` e `.githooks/pre-commit` bloqueiam os casos mais óbvios, mas não são infalíveis.
- Mudanças de arquitetura relevantes devem ser refletidas em `PLAN.md`, não só no código. Progresso concluído deve ser marcado em `ROADMAP.md` na mesma sessão de trabalho.
- Nunca usar `git commit --no-verify`/`git push --no-verify` sem confirmação explícita do usuário.
- Um clone novo do repositório precisa rodar `git config core.hooksPath .githooks` uma vez (ver `CONTRIBUTING.md`).

## Regras, hooks e skills do Cursor neste repositório

- `.cursor/rules/*.mdc` — `000-bootstrap.mdc` (protocolo de entrevista inicial, inativo desde que `bootstrap.json` está `"done"`), `010-conventions.mdc` (convenções gerais), `020-backend-python.mdc` (convenções de código Python do preset).
- `.cursor/hooks.json` — bloqueia padrões de comando claramente destrutivos e formata arquivos automaticamente após edição.
- `.cursor/skills/` — skills de ciclo de vida do dia a dia: `branch-task`, `verify-before-push`, `pr-workflow`, `release-changelog`; skills de setup (`project-bootstrap`, `stack-selector`, `repo-git-setup`, `dev-environment-setup`, `deploy-setup`, `security-baseline-audit`) já cumpriram seu papel inicial mas podem ser reusadas isoladamente.
- `.cursor/commands/start-project.md` — reexecuta a entrevista de bootstrap manualmente via `/start-project` (só use se o usuário pedir explicitamente).

## Onde encontrar mais detalhe

| Pergunta | Arquivo |
|---|---|
| O que este projeto faz e por que escolhemos essa stack/metodologia? | `PLAN.md` |
| O que falta fazer / em que fase estamos? | `ROADMAP.md` |
| Como contribuir (branch, commit, PR)? | [`CONTRIBUTING.md`](./CONTRIBUTING.md) |
| Modelo de ameaças, guardrails éticos e resposta a incidentes? | `SECURITY.md` |
| O que mudou entre versões? | [`CHANGELOG.md`](./CHANGELOG.md) |
| Como a skill em si é organizada e como o agente deve investigar? | `skill/corescope/SKILL.md` |
