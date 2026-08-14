# ROADMAP — {{PROJECT_NAME}}

Checklist de execução do projeto, fase a fase. Baseado nas decisões de [`PLAN.md`](./PLAN.md). Marque os itens conforme forem concluídos — este arquivo é a fonte da verdade sobre "o que já foi feito".

Convenção: `[ ]` pendente · `[x]` concluído · `[~]` em andamento/parcial.

---

## Fase 0 — Preparação do repositório e tooling

- [x] `PLAN.md`, `ROADMAP.md`, `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md` gerados pelo bootstrap
- [x] Regras do Cursor configuradas (`.cursor/rules/*.mdc`, incluindo as do preset de stack)
- [x] Hooks do Cursor configurados (`.cursor/hooks.json`)
- [x] Skills do Cursor configuradas (`.cursor/skills/*`)
- [x] `.gitignore` completo (segredos, artefatos de build, dependências, SO/IDE)
- [x] Hooks reais de Git criados (`.githooks/pre-commit`, `.githooks/commit-msg`)
- [x] Repositório Git inicializado, `core.hooksPath` configurado, primeiro commit
- [ ] Repositório remoto criado (GitHub) e push inicial
- [ ] Branch protection em `main` configurada (se aplicável)

## Fase 1 — Ambiente de desenvolvimento

- [ ] `Makefile` com targets `install/dev/verify/build/dist/release` funcionando
- [ ] `docker-compose.yml` para dependências locais (se aplicável) subindo sem erro
- [ ] `.env.example` completo e `make dev` funcionando com um "hello world"
- [ ] `make verify` limpo num projeto vazio (baseline antes de implementar features)

## Fase 2 — Núcleo funcional

<!-- Substituir pelos entregáveis reais do projeto, quebrados em itens pequenos e verificáveis. -->

- [ ] {{CORE_ITEM_1}}
- [ ] {{CORE_ITEM_2}}
- [ ] {{CORE_ITEM_3}}

## Fase 3 — Testes e qualidade

- [ ] Testes automatizados dos fluxos principais
- [ ] `make verify` cobrindo lint/format/build/test de forma equivalente ao CI
- [ ] Revisão de cobertura das áreas críticas ({{CRITICAL_AREA}})

## Fase 4 — Deploy e CI/CD

- [ ] `.github/workflows/ci.yml` rodando `make verify` em push/PR
- [ ] Pipeline/config de deploy para o alvo escolhido ({{DEPLOY_TARGET}}) — ver skill `deploy-setup`
- [ ] Primeiro deploy manual validado ponta a ponta
- [ ] Deploy automatizado (por tag ou push em `main`, conforme decisão registrada em `PLAN.md`)

## Fase 5 — Segurança e observabilidade

- [ ] Skill `security-baseline-audit` executada e achados revisados
- [ ] Logs estruturados no(s) componente(s) principal(is)
- [ ] Backup de dados persistentes configurado (se aplicável)
- [ ] Monitoramento básico de erros/uptime (se aplicável à escala do projeto)

## Fase 6 — Documentação final

- [ ] `README.md` com instruções finais de build/uso
- [ ] Revisão final do `PLAN.md` (marcar decisões que mudaram durante a implementação)
- [ ] `CHANGELOG.md` com a primeira release documentada (ver skill `release-changelog`)

---

## Como usar este arquivo

- Ao concluir uma tarefa, marque o checkbox correspondente na mesma sessão de trabalho (não deixe para depois).
- Se uma decisão do `PLAN.md` mudar durante a implementação, atualize o `PLAN.md` **e** ajuste os itens correspondentes aqui.
- Itens novos descobertos durante o trabalho devem ser adicionados na fase correta, não só resolvidos "silenciosamente".
