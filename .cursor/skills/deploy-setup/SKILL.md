---
name: deploy-setup
description: >-
  Monta o pipeline de CI (lint/test/build) e o deploy para o alvo de produção
  escolhido na entrevista de bootstrap (VPS próprio, Docker+registry, ou
  PaaS/serverless). Use durante o bootstrap (chamado por project-bootstrap) ou
  quando o usuário pedir para "configurar deploy"/"configurar CI".
---

# Deploy e CI/CD

## 1. CI (sempre, independente do alvo de deploy)

Copie/adapte `.cursor/templates/stacks/<preset>/ci.yml` para `.github/workflows/ci.yml`. O workflow deve, no mínimo:

1. Rodar em `push`/`pull_request` para `main`.
2. Instalar dependências (`make install`).
3. Rodar `make verify` (o mesmo gate que a skill `verify-before-push` roda localmente — isso é o que garante que "passou local" == "passa no CI").
4. Falhar o job se `make verify` falhar.

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup toolchain
        run: echo "adaptar por stack (setup-go/setup-node/setup-python)"
      - run: make install
      - run: make verify
```

## 2. Escolher o modelo de deploy conforme a resposta da entrevista

### A. VPS próprio (systemd + Nginx)

Use quando o usuário escolheu "VPS próprio" e/ou já tem um servidor.

- `deploy/systemd/<projeto>.service` — unit rodando como usuário de sistema dedicado (não root), com as capabilities mínimas necessárias.
- `deploy/nginx/<projeto>.conf` — server block com proxy para `127.0.0.1:<porta interna>`, nunca expondo o backend direto.
- Documentar em `PLAN.md` a alocação de porta/domínio (para não colidir com outros serviços no mesmo servidor, se houver).
- Deploy via SSH (workflow `.github/workflows/deploy.yml` rodando `rsync`/`scp` do artefato + `systemctl restart`), ou manual documentado em `README.md` se o usuário preferir não automatizar ainda.

```yaml
# .github/workflows/deploy.yml (esqueleto — ajustar target/secrets)
name: Deploy
on:
  push:
    tags: ["v*.*.*"]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make build
      - name: Copiar artefato para o servidor
        run: echo "scp/rsync do artefato + ssh systemctl restart <projeto>"
```

### B. Container + registry (Docker)

Use quando o alvo é cloud gerenciada ou o próprio VPS mas containerizado.

- `Dockerfile` do preset de stack, multi-stage (build separado de runtime, imagem final mínima).
- Workflow que builda e publica em `ghcr.io/<owner>/<projeto>` na tag de release.
- Deploy = `docker pull` + `docker compose up -d` no alvo (VPS) ou serviço gerenciado (ECS/Cloud Run/etc., fora do escopo genérico deste template — documentar como próximo passo manual).

### C. PaaS / serverless (Fly.io, Render, Vercel, Railway)

Use quando o usuário escolheu não gerenciar infraestrutura.

- Adicionar o arquivo de config específico da plataforma (`fly.toml`, `render.yaml`, `vercel.json` — o que existir para a stack escolhida).
- Workflow de deploy chamando o CLI da plataforma, autenticado via secret do GitHub Actions.
- Documentar em `README.md` que variáveis de ambiente de produção são configuradas no painel da plataforma, não em `.env` versionado.

## 3. Registrar a decisão

Depois de aplicar, registre em `PLAN.md`: alvo escolhido, portas/domínios (se houver), e o que o pipeline de CI/deploy faz — isso é o que a skill `security-baseline-audit` usa depois para saber o que checar.

## Não fazer

- Não exponha o backend diretamente na internet quando há um proxy (Nginx/PaaS) na frente — sempre bind em `127.0.0.1`/interface interna.
- Não deixe segredos de deploy (chaves SSH, tokens de API da plataforma) em texto plano no repositório — usar GitHub Actions secrets ou equivalente.
- Não configure deploy automático para produção a cada push em `main` sem confirmar com o usuário se é isso que ele quer (às vezes o desejado é deploy manual/por tag, ver exemplos acima usando `tags: ["v*.*.*"]`).
