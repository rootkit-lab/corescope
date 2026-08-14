# corescope

Agent Skill (Cursor/Claude) + toolkit em Python 3 para **forense de memória**, **análise estática de binários** e **engenharia reversa**. O objetivo é que o assistente de IA nunca "responda de memória" sobre uma amostra — sempre rode a ferramenta certa e cite o comando/endereço que sustenta a conclusão.

> ⚠️ **Uso ético e autorizado apenas.** Analise só amostras/sistemas que você possui ou está expressamente autorizado a examinar (laboratório próprio, CTF, engajamento de resposta a incidentes autorizado, pesquisa acadêmica). Este projeto não ajuda a produzir malware funcional nem a automatizar ataques não autorizados — ver [`SECURITY.md`](./SECURITY.md).

## Status

Em bootstrap — ver [`ROADMAP.md`](./ROADMAP.md) para o que já está pronto e o que falta (Fase 2, "Núcleo funcional", é o próximo passo real).

## O que isto é

- **Skill** (`skill/corescope/SKILL.md` + `references/`): conhecimento estruturado e hierarquizado por confiança sobre forense de memória (Volatility3), análise de binários (ELF/PE, strings/IOCs, YARA, detecção de packer) e engenharia reversa (desmontagem, emulação, execução simbólica). Empacotada como `.skill` para uso no Claude/Cursor.
- **CLI** (`corescope`): wrappers finos em Python 3 sobre ferramentas já estabelecidas da área (Volatility3, pyelftools, LIEF, capstone, yara-python, angr, unicorn), para os fluxos de triagem mais comuns.
- **Sandbox** (`Dockerfile`): ambiente isolado (sem rede por padrão) para qualquer análise dinâmica de binário não confiável — nunca execute uma amostra fora dele.

Metodologia inspirada em [`fs25-claude-skill`](https://github.com/TheCodingDad-TisonK/fs25-claude-skill): fontes hierarquizadas por confiança, `references/` organizado por domínio, arquivo de armadilhas conhecidas ("pitfalls") com selo de validação, e empacotamento da skill em `.skill`.

## Instalação

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .                 # core: CLI + skill, sem dependências pesadas
pip install -e ".[memory]"       # + volatility3 (forense de memória)
pip install -e ".[re]"           # + angr/unicorn (engenharia reversa dinâmica)
```

## Uso

```bash
corescope --help
```

Ver `skill/corescope/SKILL.md` para como o agente de IA deve rotear uma investigação, e `references/` para os guias por domínio.

## Desenvolvimento local

```bash
make install   # cria .venv e instala dependências (dev)
make dev       # smoke test da CLI
make verify    # lint + format check + testes — mesmo gate do CI
```

Ver [`CONTRIBUTING.md`](./CONTRIBUTING.md) para o fluxo de branch/commit/PR.

## Sandbox de análise dinâmica

```bash
docker build -t corescope-sandbox .
docker run --rm -it --network=none -v "$(pwd)/cases:/cases:ro" corescope-sandbox
```

Nunca rode um binário não confiável fora deste isolamento.

## Documentação

| Pergunta | Arquivo |
|---|---|
| Arquitetura e decisões (por que Volatility3, por que skill única, etc.) | [`PLAN.md`](./PLAN.md) |
| O que falta fazer / em que fase estamos | [`ROADMAP.md`](./ROADMAP.md) |
| Como contribuir (branch, commit, PR) | [`CONTRIBUTING.md`](./CONTRIBUTING.md) |
| Modelo de ameaças, uso ético e resposta a incidentes | [`SECURITY.md`](./SECURITY.md) |
| O que mudou entre versões | [`CHANGELOG.md`](./CHANGELOG.md) |

## Estrutura

```
corescope/
├── src/corescope/       # CLI + módulos de análise (mem/bin/re)
├── skill/corescope/     # SKILL.md + references/ (a skill em si)
├── tests/
├── Dockerfile           # sandbox de análise dinâmica
├── Makefile             # install/dev/verify/build/dist/release
└── .cursor/             # rules, hooks e skills de ciclo de vida (herdadas do template skink)
```

---

Gerado a partir do template [`skink`](https://github.com/rootkit-lab/skink) pela skill `project-bootstrap`.
