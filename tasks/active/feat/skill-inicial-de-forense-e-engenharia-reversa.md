---
branch: "feat/skill-inicial-de-forense-e-engenharia-reversa"
status: in-review
approved: true
pr: "https://github.com/rootkit-lab/corescope/pull/1"
created: "2026-08-13"
---

# skill inicial de forense e engenharia reversa

## Objetivo

Entregar a primeira versão real da skill `skill/corescope/` (Fase 2 do `ROADMAP.md`): conhecimento
estruturado e hierarquizado por confiança sobre forense de memória, análise estática de binários e
engenharia reversa, inspirado na metodologia do `fs25-claude-skill` (fontes por precedência,
`references/` por domínio, pitfalls com selo de validação, tool-index, empacotamento em `.skill`).
Junto, um primeiro subcomando real da CLI (`corescope bin`) para não deixar a skill sem nenhuma
implementação executável por trás.

## Escopo

- [x] `skill/corescope/SKILL.md` — frontmatter, precedência de fontes, tabela de roteamento
- [x] `references/memory-forensics/` — Volatility3 (aquisição, plugins essenciais, pslist vs psscan, malfind)
- [x] `references/binary-analysis/` — ELF/PE basics, strings/IOCs/YARA, detecção de packer
- [x] `references/reverse-engineering/` — desmontagem/decompilação, emulação, anti-anti-análise
- [x] `references/patterns/` — checklist de triagem (binário novo / dump novo)
- [x] `references/pitfalls/what-doesnt-work.md` — armadilhas conhecidas com selo ✅/⚠️/📚
- [x] `references/tool-index/` — tabela tarefa→ferramenta + receitas de busca
- [x] Implementar `corescope bin` de verdade (parsing ELF/PE real via pyelftools/pefile/LIEF), com testes
- [x] `make skill` gera `releases/corescope.skill` com sucesso
- [x] Atualizar `ROADMAP.md` (Fase 0 remoto/branch protection já feitos; marcar itens da Fase 2 concluídos)

## Fora de escopo

- `corescope mem` e `corescope re` completos (ficam como próxima task — só o roteamento/stub já existe)
- Extração de IOC/YARA scanning completo na CLI (a referência documenta o padrão; a automação total é depois)
- Publicar a primeira release (`v0.1.0`) — é a task seguinte, depois desta

## Critério de "pronto"

- `make verify` limpo (ruff + pytest)
- `make skill` gera o `.skill` sem erro
- `corescope bin <binário real>` retorna dados estruturados com evidência (não só stub)
- PR aberto, CI verde

## Log

- 2026-08-13: branch criada; escopo definido a partir do `PLAN.md`/`ROADMAP.md` recém-gerados pelo bootstrap.
- 2026-08-13: skill completa (`SKILL.md` + 11 arquivos de `references/`) escrita com base em conhecimento
  validado da área (Volatility3, pyelftools/pefile/LIEF, capstone, yara-python, angr/unicorn) — sem
  corpus fixo para "decompilar" como o `fs25-claude-skill`, então o conteúdo documenta padrões gerais
  da indústria em vez de fatos extraídos de uma fonte única.
- 2026-08-13: `corescope bin` implementado de verdade (`src/corescope/binary/analyze.py`): detecção de
  formato, hash, seções + entropia, imports, para ELF (pyelftools) e PE (pefile). Testado contra
  `/bin/true` (ELF real do sistema) e casos de erro (arquivo ausente, não-binário, ELF truncado).
- 2026-08-13: `ruff format` também formata blocos ```python dentro dos `.md` da skill — rodei
  `ruff format .` uma vez para alinhar isso antes do `make verify` ficar limpo.
- 2026-08-13: `make verify` limpo (17 testes) e `make skill` gera `releases/corescope.skill` (13 arquivos, ~21KB).
