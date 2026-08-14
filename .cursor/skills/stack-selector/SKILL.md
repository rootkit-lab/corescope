---
name: stack-selector
description: >-
  Ajuda a escolher stack técnica (linguagem, framework, banco de dados, frontend)
  para um projeto, produzindo uma tabela comparativa com trade-offs em vez de decidir
  silenciosamente. Use durante o bootstrap quando o usuário pedir recomendação de
  stack, ou depois, quando surgir uma decisão de arquitetura relevante (ex.: "Postgres
  ou SQLite?", "preciso de fila de mensagens?").
---

# Seleção de stack (com trade-offs explícitos)

Objetivo: nunca escolher uma stack "porque é a que eu conheço" sem mostrar as alternativas e o motivo real da escolha — o mesmo padrão de decisão documentada usado em `PLAN.md`.

## Como usar

1. Entenda o contexto: tipo de projeto, escala esperada, requisitos especiais (tempo real, mobile, ML, etc.), preferências que o usuário já mencionou.
2. Monte uma tabela comparativa (3-5 critérios objetivos: performance, curva de aprendizado, ecossistema/bibliotecas disponíveis, adequação ao tipo de deploy escolhido, esforço de manutenção) com 2-4 alternativas reais — não uma alternativa "de palha" fácil de descartar.
3. Recomende uma opção, mas registre a alternativa honesta (ex.: "se o objetivo fosse só entregar rápido, X resolveria em menos tempo, mas você está otimizando para Y").
4. Confirme com o usuário antes de aplicar a decisão em `PLAN.md`/preset de stack.

## Presets disponíveis no skink

Existem 4 presets prontos em `.cursor/templates/stacks/` — prefira mapear a decisão para um deles quando fizer sentido, pois já vêm com `Makefile`, CI, Dockerfile e rules configurados:

| Preset | Quando recomendar |
|---|---|
| `go-react` | Backend que precisa de performance/concorrência (APIs, ferramentas de rede/infra, binário único de deploy simples) + painel web administrativo. Bom para CLIs que depois ganham uma UI. |
| `node-ts-api` | API/backend com ecossistema JS/TS, times que já pensam em TypeScript no frontend e no backend, integração pesada com serviços de terceiros via SDKs JS. |
| `python` | Scripts, automação, dados/ML, prototipagem rápida, APIs simples onde o ecossistema Python (pandas, FastAPI, etc.) é vantagem clara. |
| `c-systems` | C de sistemas: agentes, daemons, ferramentas CLI, libs nativas — especialmente quando precisa cross-compile (Linux → Windows via mingw), TLS opcional via OpenSSL, e controle fino de memória/layout de binário. |

Se o projeto não se encaixa bem em nenhum (ex.: mobile nativo, jogos, Rust para sistemas críticos), monte a comparação normalmente e explique ao usuário que o skink não tem preset pronto para isso — a skill `dev-environment-setup`/`deploy-setup` vão precisar ser adaptadas manualmente.

## Exemplo de tabela (linguagem/framework de backend)

| Critério | Go (Fiber/Gin) | Node/TypeScript (Express/Fastify/Nest) | Python (FastAPI) |
|---|---|---|---|
| Performance/concorrência | Excelente (goroutines, binário nativo) | Boa (event loop, single-thread por padrão) | Média (GIL, mitigável com async) |
| Curva de aprendizado | Média (tipagem estática, menos "mágica") | Baixa se o time já sabe JS/TS | Baixa, muito popular |
| Ecossistema | Bom para infra/rede, menor para integrações SaaS | Enorme (npm), ideal para integrações de terceiros | Muito forte em dados/ML, bom para APIs simples |
| Deploy | Binário único, trivial de rodar em qualquer VPS | Precisa de runtime Node, mas containeriza bem | Precisa de runtime Python, containeriza bem |
| Ajuste ao skink | Preset `go-react` | Preset `node-ts-api` | Preset `python` |

Adapte critérios e alternativas ao que realmente importa para o projeto em questão — esta tabela é um ponto de partida, não uma resposta fixa.

## Outras decisões comuns que passam por esta skill

- Banco de dados: SQLite (protótipo/escala pequena, zero operação) vs. Postgres (produto em crescimento, precisa de concorrência de escrita/backup gerenciado) vs. MongoDB (dados pouco estruturados/schema variável).
- Frontend: React vs. Vue vs. "sem frontend dedicado, só API" — depende do tipo de projeto e se já existe preferência de time.
- Deploy: VPS próprio + Nginx (controle total, mais operação manual) vs. PaaS (Fly.io/Render/Railway — menos operação, menos controle) vs. cloud gerenciada (AWS/GCP — escala, mais complexidade). Ver skill `deploy-setup` para o que cada opção implica em CI/CD.

## Não fazer

- Não decida a stack sem apresentar a comparação ao usuário quando ele pediu recomendação — mesmo que a resposta "óbvia" pareça clara para você.
- Não invente números de benchmark específicos sem ressalvar que são estimativas gerais, não medições feitas para este projeto.
