# ROADMAP — corescope

Checklist de execução do projeto, fase a fase. Baseado nas decisões de [`PLAN.md`](./PLAN.md). Marque os itens conforme forem concluídos — este arquivo é a fonte da verdade sobre "o que já foi feito".

Convenção: `[ ]` pendente · `[x]` concluído · `[~]` em andamento/parcial.

---

## Fase 0 — Preparação do repositório e tooling

- [x] `PLAN.md`, `ROADMAP.md`, `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md` gerados pelo bootstrap
- [x] Regras do Cursor configuradas (`.cursor/rules/*.mdc`, incluindo as do preset Python)
- [x] Hooks do Cursor configurados (`.cursor/hooks.json`)
- [x] Skills do Cursor configuradas (`.cursor/skills/*`)
- [x] `.gitignore` completo (segredos, artefatos de build, amostras/dumps de casos)
- [x] Hooks reais de Git criados (`.githooks/pre-commit`, `.githooks/commit-msg`)
- [x] Repositório Git inicializado, `core.hooksPath` configurado, primeiro commit
- [ ] Repositório remoto criado (GitHub `rootkit-lab/corescope`, público) e push inicial
- [ ] Branch protection em `main` configurada

## Fase 1 — Ambiente de desenvolvimento

- [x] `Makefile` com targets `install/dev/verify/build/dist/release` funcionando
- [x] `.env.example` completo e `make dev` funcionando com um "hello world" (CLI `--help`)
- [x] `make verify` limpo num projeto vazio (baseline antes de implementar features)
- [ ] Extras opcionais (`corescope[memory]`, `corescope[re]`) documentados e testados numa venv separada

## Fase 2 — Núcleo funcional (skill + CLI)

- [ ] `skill/corescope/SKILL.md` com tabela de precedência de fontes e tabela de roteamento por domínio
- [ ] `references/memory-forensics/` — aquisição de dump, plugins essenciais do Volatility3, artefatos (processos, rede, injeção)
- [ ] `references/binary-analysis/` — parsing ELF/PE, strings/IOCs, YARA, detecção de packer/anti-análise
- [ ] `references/reverse-engineering/` — desmontagem/decompilação, emulação (`unicorn`), execução simbólica (`angr`), anti-anti-debug
- [ ] `references/patterns/` — receitas validadas por tarefa comum
- [ ] `references/pitfalls/what-doesnt-work.md` — armadilhas conhecidas com selo de validação
- [ ] `references/tool-index/` — qual ferramenta usar para qual pergunta + receitas de busca/grep
- [ ] CLI `corescope mem|bin|re` com pelo menos um subcomando funcional por domínio
- [ ] `skill/package_skill.py` — empacota `skill/corescope/` em `.skill`; `make dist` chama esse script
- [ ] Guardrail ético/legal explícito no `SKILL.md` e no `README.md` (uso autorizado apenas)

## Fase 3 — Testes e qualidade

- [ ] Testes automatizados dos fluxos principais da CLI (`tests/test_cli.py`, `tests/test_binary.py`, ...)
- [ ] `make verify` cobrindo lint/format/build/test de forma equivalente ao CI
- [ ] Revisão de cobertura das áreas críticas (parsing de binário não confiável — nunca deve travar/crashar com input malformado)

## Fase 4 — Distribuição e CI/CD

- [ ] `.github/workflows/ci.yml` rodando `make verify` em push/PR
- [ ] Release publica wheel + `.skill` como anexos da GitHub Release (ver skill `release-changelog`)
- [ ] Primeira release `v0.1.0` validada ponta a ponta (instalação via `pip install` + skill carregada no Cursor/Claude)

## Fase 5 — Segurança e observabilidade

- [ ] Skill `security-baseline-audit` executada e achados revisados
- [ ] Confirmar que nenhuma amostra/dump real de caso está versionada (auditoria manual do histórico antes da primeira release pública)
- [ ] `Dockerfile` sandbox documentado e testado (`--network=none`, volume read-only)

## Fase 6 — Documentação final

- [ ] `README.md` com instruções finais de instalação/uso da CLI e da skill
- [ ] Revisão final do `PLAN.md` (marcar decisões que mudaram durante a implementação)
- [ ] `CHANGELOG.md` com a primeira release documentada (ver skill `release-changelog`)

---

## Como usar este arquivo

- Ao concluir uma tarefa, marque o checkbox correspondente na mesma sessão de trabalho (não deixe para depois).
- Se uma decisão do `PLAN.md` mudar durante a implementação, atualize o `PLAN.md` **e** ajuste os itens correspondentes aqui.
- Itens novos descobertos durante o trabalho devem ser adicionados na fase correta, não só resolvidos "silenciosamente".
