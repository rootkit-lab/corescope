---
name: project-bootstrap
description: >-
  Orquestra a inicialização de um projeto novo a partir do template skink: entrevista
  o usuário sobre o que vai ser construído e gera PLAN.md, ROADMAP.md, SECURITY.md,
  o preset de stack, o ambiente de dev, o CI/deploy e o Git completo. Use sempre que
  .cursor/state/bootstrap.json tiver status "pending", no início da primeira conversa
  de um projeto novo, ou quando o usuário pedir explicitamente para (re)iniciar o
  bootstrap / rodar /start-project.
---

# Bootstrap de projeto

Esta é a skill orquestradora do template `skink`. Ela transforma o template genérico num projeto real, através de uma entrevista curta seguida de geração automática de documentação, stack, ambiente de dev, deploy e Git.

## Quando usar

- `.cursor/state/bootstrap.json` tem `"status": "pending"` (verificação obrigatória no início de qualquer conversa — ver `.cursor/rules/000-bootstrap.mdc`).
- O usuário invoca `/start-project`.
- O usuário pede explicitamente para "recomeçar"/"reconfigurar o projeto do zero".

**Não** avance para implementação de código de negócio antes de completar esta skill até o fim (ou o usuário pedir explicitamente para só planejar).

## Passo 1 — Entrevista

Use a ferramenta de perguntas estruturadas (`AskQuestion` ou equivalente) sempre que disponível, em vez de perguntar tudo em texto livre. Pode agrupar perguntas relacionadas na mesma chamada. Roteiro:

1. **Nome do projeto** e **uma frase** descrevendo o problema que ele resolve.
2. **Tipo de projeto**: web app full-stack, API/backend, CLI, biblioteca, app desktop, app mobile, infraestrutura/sistema, dados/ML, outro (texto livre).
3. **Stack**:
   - Opção A: usuário já sabe o que quer → mapear para um preset existente (`go-react`, `node-ts-api`, `python`) se possível, ou anotar como "customizado" se não bater com nenhum.
   - Opção B: usuário pede recomendação → invocar a skill `stack-selector`, apresentar a tabela comparativa, e só seguir depois que o usuário confirmar a escolha.
4. **Onde vai rodar em produção**: VPS próprio, cloud gerenciada (AWS/GCP/Azure/DigitalOcean), PaaS/serverless (Fly.io/Render/Vercel/Railway), on-premise/uso local apenas, "ainda não sei" (nesse caso, recomende com base no tipo de projeto e escala).
5. **Escala esperada**: protótipo/uso pessoal, produto pequeno em produção, produto que precisa escalar bastante.
6. **Requisitos de segurança/compliance especiais**: dados sensíveis, LGPD/GDPR, nenhum em particular, outro.
7. **GitHub com CI/CD e branch protection?** sim (recomendado) / não, manter simples por enquanto.
8. **Idioma de docs e convenção de identificadores**: confirmar se mantém o padrão do template (docs em pt-BR, identificadores de código em inglês) ou se o usuário quer outro idioma.

Se o usuário já tiver respondido parte disso na mensagem que invocou a skill (ex.: `/start-project um SaaS de agendamento em Node/TS`), não repita essas perguntas — confirme o que foi entendido e pergunte só o que falta.

## Passo 2 — Gerar documentação do projeto

A partir das respostas, preencha os templates em `.cursor/templates/docs/` e grave o resultado **na raiz do projeto** (esses arquivos não existem antes do bootstrap):

- `.cursor/templates/docs/PLAN.template.md` → `PLAN.md` — arquitetura, decisões com tabela comparativa (reaproveite a saída da skill `stack-selector` se foi usada), alocação de portas/domínios se houver deploy em servidor próprio.
- `.cursor/templates/docs/ROADMAP.template.md` → `ROADMAP.md` — checklist de fases adaptado ao tipo/escala do projeto.
- `.cursor/templates/docs/SECURITY.template.md` → `SECURITY.md` — modelo de ameaças, ajustado aos requisitos de segurança respondidos no passo 1.

Depois, atualize (não recrie do zero) os arquivos que já existem no template:

- `README.md` — substitua a seção sobre o skink por uma descrição real do projeto (o que é, como rodar, stack, status).
- `AGENTS.md` — remova o protocolo de bootstrap do topo (ou marque como concluído) e preencha as seções de fatos/convenções com os dados reais do projeto.
- `CHANGELOG.md` — adicione entrada em `[Unreleased]` registrando a criação do projeto a partir do skink.

## Passo 3 — Aplicar o preset de stack

Se um preset (`go-react`, `node-ts-api`, `python`) foi escolhido ou é a melhor aproximação:

1. Copie `.cursor/templates/stacks/<preset>/rules/*.mdc` para `.cursor/rules/` (numerando depois das rules `000-`/`010-` já existentes, ex.: `020-backend.mdc`).
2. Copie `Makefile`, `Dockerfile`, `docker-compose.yml` (se houver) e `.env.example` do preset para a raiz do projeto, ajustando nomes/portas/variáveis ao projeto real.
3. Copie o `ci.yml` do preset para `.github/workflows/ci.yml` (criar a pasta se não existir).

Se nenhum preset bater bem (stack "customizada"), monte manualmente uma estrutura equivalente (rules stack-agnósticas removidas/ajustadas, `Makefile` com os mesmos targets `dev/verify/build/dist/release`, CI mínimo) — não deixe o projeto sem nenhum desses pontos só porque não havia preset pronto.

## Passo 4 — Ambiente de dev, deploy e segurança

Nesta ordem, execute (ou oriente o usuário a executar, se depender de credenciais que você não tem):

1. Skill `dev-environment-setup` — monta `docker-compose.yml`/`.env.example`/estrutura inicial de pastas para rodar localmente.
2. Skill `deploy-setup` — monta CI (lint/test/build) e o pipeline/instruções de deploy para o alvo escolhido no passo 1.
3. Skill `repo-git-setup` — inicializa o Git do projeto (histórico novo, não herdado do skink), configura hooks, primeiro commit, e opcionalmente cria o repositório remoto com branch protection.
4. Se o projeto vai rodar em infraestrutura própria (VPS) ou tem requisitos de segurança elevados: mencione a skill `security-baseline-audit` como próximo passo recomendado (não precisa rodar agora, pois normalmente ainda não há nada provisionado).

## Passo 5 — Finalizar

1. Atualize `.cursor/state/bootstrap.json`:

```json
{
  "status": "done",
  "project_name": "<nome informado>",
  "project_type": "<tipo informado>",
  "stack_preset": "<preset ou \"custom\">",
  "deploy_target": "<alvo de deploy informado>",
  "bootstrapped_at": "<data/hora ISO 8601 atual>"
}
```

2. Resuma para o usuário, em poucas linhas: o que foi criado, onde estão as decisões (`PLAN.md`), o que falta (`ROADMAP.md`), e qual é o próximo passo natural (geralmente: skill `branch-task` para começar a primeira feature real).

## Não fazer

- Não gere código de negócio (rotas, componentes, lógica de domínio) durante o bootstrap — o objetivo é preparar o terreno, não implementar a primeira feature.
- Não marque `.cursor/state/bootstrap.json` como `"done"` se algum passo essencial (docs, stack, git) não foi concluído — melhor deixar `"pending"` e explicar o que falta do que fingir que terminou.
- Não sobrescreva `PLAN.md`/`ROADMAP.md`/`SECURITY.md` já preenchidos sem confirmação explícita do usuário.
