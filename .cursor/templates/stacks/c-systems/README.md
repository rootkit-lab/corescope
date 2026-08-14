# Preset: c-systems

C de sistemas (agentes, daemons, ferramentas CLI, libs nativas) com cross-compile via mingw (Linux → Windows), TLS opcional via OpenSSL, testes com Unity, e tooling de qualidade (clang-format, cppcheck, clang-tidy). Baseado em padrões extraídos de projetos C maduros e generalizados.

## Quando usar este preset

- Ferramenta CLI em C que precisa rodar em Linux e Windows.
- Agente/daemon nativo com TLS opcional.
- Lib nativa cross-platform com binários para múltiplos alvos.
- **Não** é para: apps com GUI nativa (use Electron/Tauri/Wails), serviços de rede de alto nível (use Go/Node), scripts rápidos (use Python).

## O que este preset traz

| Arquivo | Função |
|---|---|
| `Makefile` | Build native + cross-compile (mingw), targets `install/dev/verify/build/dist/release`, seleção de stubs |
| `.clangd` | IntelliSense cross-target no editor (clangd LSP) |
| `.clang-format` | Formatação consistente |
| `.clang-tidy` | Lint/estática avançada |
| `cppcheck.cfg` | Análise estática complementar |
| `Dockerfile` | Build reprodutível em container (opcional) |
| `ci.yml` | GitHub Actions com matriz: gcc/clang native + mingw cross |
| `.env.example` | Variáveis de runtime |
| `rules/c-systems.mdc` | Convenções de código C |
| `scripts/build-openssl-mingw.sh` | Bootstrap de OpenSSL estático para cross-compile (opcional) |
| `tests/` | Esqueleto com Unity (framework de testes) |
| `include/` + `src/` | Estrutura inicial com exemplo hello world + stub TLS |

## Estrutura sugerida

```
include/                  # headers públicos (com *_H guards)
  <projeto>/
    config.h
    transport.h
src/
  core/                    # main, config, logger
  transport/
    transport_tls.c        # wrapper OpenSSL (ou _stub.c se NO_TLS_STUB)
    transport_tls_stub.c
  <domínio>/
third_party/              # deps estáticas (buildadas por scripts/)
tests/
  test_main.c              # Unity runner
  test_<módulo>.c
```

## Aplicar este preset (feito pela skill dev-environment-setup)

1. Copiar `Makefile`, `.clangd`, `.clang-format`, `.clang-tidy`, `cppcheck.cfg`, `.env.example` para a raiz do projeto.
2. Copiar `rules/*.mdc` para `.cursor/rules/`.
3. Copiar `ci.yml` para `.github/workflows/ci.yml`.
4. Copiar `Dockerfile` para a raiz (opcional).
5. Copiar `scripts/build-openssl-mingw.sh` para `scripts/` (só se for usar TLS cross-compile).
6. Criar `include/` e `src/` com a estrutura sugerida (esqueleto hello world já vem pronto).
7. Copiar `tests/` com Unity (já incluso um teste de exemplo).

## TLS opcional (padrão de stub)

O wrapper TLS (`src/transport/transport_tls.c`) compila de duas formas:

- **Sem `WINDOWS_TLS=1`** (default): usa `transport_tls_stub.c` — todas as chamadas retornam erro `ENOSYS`, mas o projeto compila e linka sem OpenSSL. Útil para protótipos sem rede ou alvos sem TLS.
- **Com `WINDOWS_TLS=1`**: usa `transport_tls.c` com OpenSSL — requer `third_party/openssl-mingw/prefix/` (construído por `scripts/build-openssl-mingw.sh`) ou OpenSSL do sistema.

O mesmo padrão vale para qualquer feature opcional: crie `foo.c` + `foo_stub.c` e selecione no Makefile por flag.

## Testes com Unity

Unity é um framework de testes C minimalista (do ThrowTheSwitch). O preset já vem com:

- `tests/unity/` — sources do Unity (Unity.c, Unity.h, UnityInt.c) — pinado a uma versão.
- `tests/test_main.c` — runner que chama todos os `test_*` functions.
- `make test` — compila e roda os testes.

Adicione novos testes em `tests/test_<módulo>.c` e registre em `test_main.c`.
