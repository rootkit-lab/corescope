# Preset: node-ts-api

API/backend em Node.js + TypeScript. Bom para times que já pensam em TS no frontend e no backend, ou integrações pesadas com SDKs JS de terceiros.

## O que este preset traz

- `Makefile` — wrapper fino sobre scripts `npm`, expondo os targets padrão `install/dev/verify/build/dist/release`.
- `Dockerfile` — multi-stage: build TypeScript → imagem final `node:alpine` só com `dist/` + `node_modules` de produção.
- `ci.yml` — GitHub Actions com `setup-node`, roda `make verify`.
- `.env.example` — variáveis mínimas.
- `rules/backend-node.mdc` — convenções de código.

## Estrutura sugerida

```
src/
├── routes/       # handlers HTTP
├── services/     # lógica de negócio
├── db/           # acesso a dados
└── index.ts
```

## Aplicar este preset (feito pela skill dev-environment-setup)

1. Copiar `Makefile`, `Dockerfile`, `.env.example` para a raiz do projeto.
2. Copiar `rules/*.mdc` para `.cursor/rules/`.
3. Copiar `ci.yml` para `.github/workflows/ci.yml`.
4. `npm init -y` + instalar framework escolhido (Express/Fastify/Nest) se ainda não existir `package.json`.
5. Garantir que `package.json` tenha os scripts: `dev`, `build`, `lint`, `test`, `start` — o `Makefile` chama esses scripts.
