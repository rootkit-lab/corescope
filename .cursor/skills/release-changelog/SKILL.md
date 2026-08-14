---
name: release-changelog
description: >-
  Prepara e publica uma release: valida que [Unreleased] do CHANGELOG.md está
  preenchido, bump de versão semver, cria a tag e dispara o workflow de release do
  CI. Use quando o usuário pedir release, changelog, notas de versão, ou tag vX.Y.Z.
---

# Release + Changelog

## Arquivos envolvidos

| Path | Função |
|---|---|
| `CHANGELOG.md` | Histórico user-facing (Keep a Changelog) |
| `.cursor/skills/release-changelog/scripts/prepare-release.sh` | Fluxo completo: valida → tag → push |
| `.github/workflows/release.yml` | Build + publica release no GitHub (gerado pela skill `deploy-setup`) |

## 1. Preencher `[Unreleased]`

Antes de qualquer release, `CHANGELOG.md` precisa ter a seção `[Unreleased]` preenchida com o que mudou desde a última versão, em linguagem clara para o usuário final (sem jargão de desenvolvedor, sem hash de commit):

```markdown
## [Unreleased]

### Added
- Funcionalidade nova X

### Changed
- Melhoria de UX/performance em Y

### Fixed
- Correção do bug Z

### Notas para atualização
- Passos que quem já usa a versão anterior precisa saber (se houver)
```

Use apenas as subseções que fizerem sentido (não force `Changed`/`Fixed` vazios).

## 2. Decidir o bump de versão (SemVer)

- `MAJOR` — mudança incompatível/breaking change.
- `MINOR` — funcionalidade nova, compatível.
- `PATCH` — correção de bug, sem funcionalidade nova.

## 3. Publicar

```bash
.cursor/skills/release-changelog/scripts/prepare-release.sh --version X.Y.Z
# ou --dry-run primeiro, para revisar sem efeitos colaterais
```

O script:
1. Confirma que `[Unreleased]` não está vazio.
2. Confirma working tree limpo (sem alterações não commitadas).
3. Move o conteúdo de `[Unreleased]` para uma nova seção `## [X.Y.Z] - <data>` no `CHANGELOG.md`, deixando `[Unreleased]` vazio de novo.
4. Comita (`chore(release): vX.Y.Z`) e cria a tag `vX.Y.Z`.
5. `git push origin main --tags` — a tag dispara `.github/workflows/release.yml`.

## 4. Acompanhar o workflow de release

```bash
.cursor/skills/pr-workflow/scripts/monitor-ci.sh --workflow Release --watch
```

Se falhar: corrigir no branch normal (`branch-task` → fix → PR), e então criar uma tag nova (releases não se "editam" depois de publicadas) ou usar `workflow_dispatch` se o problema for só de build/notas, não de código.

## Erros comuns

| Erro | Causa | Solução |
|---|---|---|
| `[Unreleased] vazio` | Changelog não preenchido antes do release | Preencher antes de rodar o script |
| `tag já existe` | Versão já publicada | Bump para a próxima versão |
| `working tree sujo` | Alterações não commitadas | Commit/stash antes de liberar |

## Não fazer

- Não editar seções já publicadas do `CHANGELOG.md` (só `[Unreleased]`) — histórico de release é imutável.
- Não usar `--no-verify` no push de release.
- Não commitar/tagear sem pedido explícito do usuário.
