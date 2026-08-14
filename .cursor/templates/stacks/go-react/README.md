# Preset: go-react

Backend em Go + painel/frontend em React, servido embutido no mesmo binário (`embed.FS`). Bom para APIs que precisam de performance/concorrência e um binário único de deploy simples (VPS ou container).

## O que este preset traz

- `Makefile` — targets `install/dev/verify/build/dist/release`.
- `Dockerfile` — multi-stage: build do frontend (Vite) → build do binário Go com o frontend embutido → imagem final `distroless`/`alpine` mínima.
- `docker-compose.yml` — Postgres para dependências locais (remover se o projeto não precisar de banco).
- `ci.yml` — GitHub Actions: `setup-go` + `setup-node`, roda `make verify`.
- `.env.example` — variáveis mínimas (porta, DSN do banco, JWT secret).
- `rules/backend-go.mdc`, `rules/frontend-react.mdc` — convenções de código.

## Estrutura sugerida

```
cmd/<projeto>/main.go
internal/
├── api/        # handlers HTTP
├── store/      # acesso a dados
└── config/
web/            # frontend React+Vite+TS, build embutido via go:embed
```

## Aplicar este preset (feito pela skill dev-environment-setup)

1. Copiar `Makefile`, `Dockerfile`, `docker-compose.yml`, `.env.example` para a raiz do projeto.
2. Copiar `rules/*.mdc` para `.cursor/rules/`.
3. Copiar `ci.yml` para `.github/workflows/ci.yml`.
4. `go mod init <module>` e `npm create vite@latest web -- --template react-ts` (ou equivalente) se ainda não existirem.
