---
branch: "feat/corescope-mem-e-re-implementacoes-reais"
status: done
approved: true
pr: "https://github.com/rootkit-lab/corescope/pull/3"
created: "2026-08-14"
---

# corescope mem e re: implementacoes reais

## Objetivo

`corescope mem` e `corescope re` ainda eram stub (só `corescope bin` era real). Implementar
os dois de verdade, mantendo o mesmo princípio do resto do projeto: wrapper fino, evidência
sempre junto do dado, sem fingir mais inteligência do que a ferramenta de fato tem.

## Escopo

- [x] `corescope mem` — wrapper fino sobre o CLI `vol` (Volatility3): roda plugin(s), retorna
      stdout/stderr + o comando exato executado como evidência; detecção simples de OS
      (`windows.info`/`linux.info`) para escolher plugins de triagem default (pslist/psscan
      ou pslist/psaux) quando `--plugin` não é passado
- [x] Erro claro (não traceback) quando `vol` não está instalado, com dica de
      `pip install "corescope[memory]"`
- [x] `corescope re` — desmontagem real do entry point via `capstone`, reaproveitando detecção
      de formato ELF/PE já existente em `corescope.binary.analyze`; mapeamento de arquitetura
      (x86/x86_64/ARM/ARM64) para os modos do capstone
- [x] Testes: `mem` com runner injetado (fake), sem depender de `vol`/dump real; `re` contra
      `/bin/true` (ELF real do sistema, já usado em `test_binary_analyze.py`)
- [x] Testes de erro: arquivo ausente, formato não suportado, arquitetura não suportada
- [x] `make verify` limpo; atualizar `ROADMAP.md` (Fase 2: CLI totalmente funcional)

## Fora de escopo

- Integração com a API interna do Volatility3 (ficamos no CLI `vol`, não no framework Python)
- `angr`/`unicorn` (execução simbólica, emulação) — fica para uma task futura; `re` por
  enquanto é "desmontagem do entry point", não análise dinâmica
- Detecção de OS via assinatura de kernel mais robusta que "tentar `.info` de cada OS"

## Critério de "pronto"

- `corescope mem <dump>` e `corescope re <path>` funcionam ponta a ponta contra uma amostra
  real (dump sintético/mockado para mem — não temos um dump real versionável; ELF real para re)
- `make verify` limpo
- PR aberto, CI verde

## Log

- 2026-08-13: branch criada a partir do pedido de continuar depois do merge da skill inicial.
- 2026-08-13: `corescope re` implementado e validado contra `/bin/true` — desmontagem via
  capstone no entry point bate exatamente com `objdump -d --start-address=0x19f0` (mesmos
  endereços/instruções), confirmado manualmente antes de escrever os testes.
- 2026-08-13: `corescope mem` implementado como wrapper do CLI `vol`, nunca da API interna do
  Volatility3 (mantém a evidência = comando real executado). Como não há `vol`/dump real
  disponível neste ambiente (dependência pesada, extra opcional), os testes injetam um
  `runner` fake — `_default_runner` real só é exercitado no teste que confirma o erro
  amigável quando `vol` não está instalado (`VolatilityNotAvailableError`).
- 2026-08-13: `make verify` limpo (36 testes) com os dois módulos novos.
