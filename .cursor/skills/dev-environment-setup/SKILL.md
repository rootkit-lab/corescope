---
name: dev-environment-setup
description: >-
  Monta o ambiente de desenvolvimento local do projeto: Makefile com targets
  padronizados (dev/verify/build/dist/release), docker-compose para dependências
  (banco de dados, etc.), .env.example e estrutura inicial de pastas. Use durante o
  bootstrap (chamado por project-bootstrap) ou quando o usuário pedir para "montar o
  ambiente de dev"/"rodar o projeto localmente" e isso ainda não existir.
---

# Ambiente de desenvolvimento local

Objetivo: qualquer pessoa (ou agente) consegue rodar o projeto localmente com poucos comandos, e as skills de ciclo de vida (`verify-before-push`, `pr-workflow`, `release-changelog`) funcionam sem precisar saber qual stack foi escolhida — porque tudo passa por `make <target>`.

## 1. Copiar a base do preset de stack

Se um preset foi escolhido no bootstrap (`go-react`/`node-ts-api`/`python`), copie para a raiz do projeto:

- `Makefile` do preset (`.cursor/templates/stacks/<preset>/Makefile`)
- `docker-compose.yml` (se o preset tiver — normalmente para banco de dados/dependências, não para a aplicação em si durante o dev)
- `.env.example`

Ajuste nomes de serviço, portas e variáveis para o projeto real (nunca deixe placeholders genéricos tipo `myapp` no arquivo final).

## 2. Contrato mínimo do `Makefile`

Independente da stack, o `Makefile` gerado **precisa** expor estes targets (as outras skills dependem disso):

| Target | Faz o quê |
|---|---|
| `make install` | Instala dependências (primeira vez / após mudança de lockfile) |
| `make dev` | Roda o projeto localmente com hot-reload (quando aplicável) |
| `make verify` | Format check + lint/vet + build + testes — o gate local equivalente ao CI |
| `make build` | Build de produção |
| `make dist` | Empacota o artefato final (binário/imagem/bundle), se aplicável |
| `make release VERSION=X.Y.Z` | Aciona o fluxo da skill `release-changelog` |

Se a stack escolhida não tiver `make` disponível no ambiente alvo (raro), documente em `README.md` o comando equivalente (`npm run` / `task` / etc.) mas mantenha os mesmos nomes de target por consistência.

## 3. Dependências externas via `docker-compose`

Se o projeto precisa de banco de dados/cache/fila para rodar localmente (Postgres, Redis, etc.), gere um `docker-compose.yml` mínimo só com essas dependências — a aplicação em si normalmente roda direto no host durante o dev (mais rápido para hot-reload), não dentro do compose:

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    ports:
      - "5432:5432"
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

Adapte a imagem/variáveis à decisão registrada em `PLAN.md`. Se o projeto não precisa de nenhuma dependência externa, não crie `docker-compose.yml` só para existir.

## 4. `.env.example`

Toda variável de ambiente que o projeto usa deve ter uma entrada correspondente em `.env.example` (sem valores reais/segredos — usar placeholders óbvios como `changeme`). Nunca commitar o `.env` real (já bloqueado por `.gitignore` e pelo hook `pre-commit`).

## 5. Estrutura inicial de pastas

Crie a estrutura mínima que o preset de stack sugere (ver `README.md` de cada preset em `.cursor/templates/stacks/<preset>/`), o suficiente para `make dev` funcionar com um "hello world" — não implemente funcionalidades de negócio aqui, isso é trabalho da primeira task real (skill `branch-task`).

## 6. Validar

Depois de montar tudo:

```bash
make install
make dev     # confirmar que sobe sem erro, então interromper
make verify  # confirmar que os gates básicos passam mesmo num projeto vazio
```

Se `make verify` falhar num projeto recém-criado, corrija antes de seguir para as próximas skills — não é aceitável entregar o ambiente de dev já quebrado.

## Não fazer

- Não crie `docker-compose.yml` para a aplicação em si se o objetivo é dev local rápido com hot-reload — reserve container da app para `deploy-setup`/produção.
- Não deixe `.env.example` incompleto — toda env var usada no código deve aparecer lá.
- Não pule a validação do passo 6 e siga para as próximas skills com o ambiente quebrado.
