# Política de Segurança — corescope

Modelo de ameaças, garantias de design e procedimento de resposta a incidentes. Complementa as decisões justificadas em [`PLAN.md`](./PLAN.md).

## Requisitos levantados na entrevista de bootstrap

Domínio sensível por natureza: forense de memória, análise de binários e engenharia reversa tocam diretamente em técnicas usadas tanto por defensores quanto por atacantes. O requisito central não é conformidade regulatória (a ferramenta não processa dados pessoais de terceiros por padrão — roda localmente, sob controle do próprio analista), e sim **uso ético e autorizado**: o projeto existe para analisar amostras/sistemas, não para produzir malware funcional ou automatizar ataques não autorizados.

## Modelo de ameaças (resumo)

- **Ponto central de confiança:** o host onde o analista roda a CLI/skill. Não há servidor, banco de dados ou provedor de identidade — é uma ferramenta local.
- **O que acontece se o host for comprometido:** o vetor mais provável não é uma falha do `corescope` em si, mas o analista **executar uma amostra maliciosa fora do sandbox isolado** durante análise dinâmica. Ver garantia "Sandbox obrigatório" abaixo.
- **Dados sensíveis processados:** memory dumps e binários de um caso real podem conter segredos (senhas em texto claro na RAM, chaves privadas, tokens, dados pessoais). Esses artefatos **nunca** devem ser commitados no repositório nem logados pela CLI.
- **Atores privilegiados:** só o próprio operador local; não há múltiplos usuários nem controle de acesso a revogar.

## Garantias de design

| Garantia | Como é implementada |
|---|---|
| Segredos nunca versionados | `.gitignore` + hook `.githooks/pre-commit` bloqueiam os casos mais óbvios |
| Nenhuma amostra/dump real de caso versionado | `.gitignore` cobre `samples/`, `cases/`, `*.dmp`, `*.vmem`, `*.raw`, `*.mem`; revisão manual do diff antes de qualquer commit que toque esses diretórios |
| Análise dinâmica sempre isolada | `Dockerfile` sandbox dedicado; uso documentado com `docker run --network=none` e amostra montada read-only |
| Escopo ético explícito | `skill/corescope/SKILL.md` e `README.md` recusam pedidos de criação de malware funcional ou de ataque a sistemas sem autorização — mesmo padrão de guardrail já usado nas skills pessoais do autor (ex.: `html-scraping`) |
| Toda afirmação técnica é verificável | A skill e a CLI sempre citam o comando/endereço/offset que sustenta uma conclusão — nunca "conclusões de memória" sem evidência local |

## O que NÃO fazer (violação das garantias acima)

- Nunca executar/desempacotar um binário não confiável fora do `Dockerfile` sandbox isolado.
- Nunca ajudar a produzir malware funcional, exploit weaponizado, ou automação de ataque contra sistema que o usuário não possui ou não está expressamente autorizado a testar.
- Nunca commitar amostras de malware reais, memory dumps de máquinas de terceiros, ou dados de casos/clientes no repositório (que é público).
- Nunca fazer bind de qualquer serviço auxiliar (ex.: um servidor de debug local) em `0.0.0.0` — sempre `127.0.0.1` se algo do tipo existir.
- Nunca desabilitar o isolamento de rede do sandbox (`--network=none`) "só para testar mais rápido" sem necessidade concreta e revisão do que está sendo exposto.

## Hardening aplicado/planejado

Ver checklist completo em [`ROADMAP.md`](./ROADMAP.md) — Fase 5. Use a skill `security-baseline-audit` para revalidar periodicamente, com atenção extra a: arquivos de amostra esquecidos no histórico do Git antes de qualquer release pública.

## Rotação e revogação de credenciais

- Este projeto não mantém segredos de longa duração além de tokens de CI (ex.: publicação de release no GitHub Actions, se configurado). Rotacionar via GitHub → Settings → Secrets caso haja suspeita de exposição.
- Token pessoal do `gh` CLI usado durante o bootstrap pertence ao ambiente do operador, não ao projeto — nada a rotacionar aqui.

## Resposta a incidentes (procedimento de emergência)

Se houver suspeita real de comprometimento (ex.: uma amostra escapou do sandbox, ou uma máquina foi infectada durante análise):

1. **Isolar**: desconectar a máquina afetada da rede imediatamente; não confiar em nenhum processo/binário local para diagnosticar o próprio comprometimento.
2. **Rotacionar credenciais**: qualquer segredo/token/chave presente na máquina afetada (mesmo que não relacionado ao `corescope`).
3. **Auditar**: revisar qual amostra estava em análise, se o sandbox estava de fato ativo (`--network=none`), e os logs disponíveis.
4. **Reconstruir**: preferir reprovisionar a máquina/VM afetada a "limpar" — é a prática padrão em resposta a incidentes de malware.

## Reportando um problema de segurança

Como este é um repositório público, **não abra uma issue pública** para uma vulnerabilidade real na ferramenta (ex.: um binário malformado que trava a CLI de forma explorável). Use o recurso de "Report a vulnerability" do GitHub (Settings → Security → Security advisories) no repositório `rootkit-lab/corescope`.
