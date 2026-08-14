# tests/

Testes do projeto C usando [Unity](https://github.com/ThrowTheSwitch/Unity) (framework minimalista de testes C).

## Setup

O Unity não é vendido junto com o preset — é baixado por um script de bootstrap:

```bash
make install   # roda scripts/build-unity.sh automaticamente
```

Ou manualmente:

```bash
scripts/build-unity.sh
```

Isso baixa Unity v2.5.2 e coloca em `tests/unity/` (já no `.gitignore` do preset — não commitar).

## Rodar

```bash
make test
```

## Adicionar testes

1. Crie `tests/test_<módulo>.c` com funções `test_*`.
2. Adicione `RUN_TEST(test_<nome>)` em `tests/test_main.c`.
3. O Makefile detecta `tests/test_*.c` automaticamente — não precisa registrar em mais nada.

## Convenção

- Um teste por comportamento, não um teste por função.
- Todo bug fix vem com teste que reproduz o caso (ver `.cursor/rules/c-systems.mdc`).
- Não testar via `printf` — usar as macros do Unity (`TEST_ASSERT_*`).
