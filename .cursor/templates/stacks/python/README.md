# Preset: python

Backend/API simples, automação, scripts, dados/ML. Usa `venv` + `pip` por padrão (trocar por `uv`/`poetry` é uma adaptação direta se o usuário preferir).

## O que este preset traz

- `Makefile` — targets `install/dev/verify/build/dist/release`.
- `Dockerfile` — multi-stage: instala dependências → imagem final `python:slim` mínima.
- `ci.yml` — GitHub Actions com `setup-python`, roda `make verify`.
- `.env.example` — variáveis mínimas.
- `rules/backend-python.mdc` — convenções de código.

## Estrutura sugerida

```
src/<pacote>/
├── api/          # rotas (se usar FastAPI/Flask)
├── services/
└── __init__.py
tests/
```

## Aplicar este preset (feito pela skill dev-environment-setup)

1. Copiar `Makefile`, `Dockerfile`, `.env.example` para a raiz do projeto.
2. Copiar `rules/*.mdc` para `.cursor/rules/`.
3. Copiar `ci.yml` para `.github/workflows/ci.yml`.
4. Criar `requirements.txt` (ou `pyproject.toml`) e `venv` se ainda não existirem.
5. Garantir `ruff` (lint+format) e `pytest` nas dependências de desenvolvimento.
