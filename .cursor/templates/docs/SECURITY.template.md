# Política de Segurança — {{PROJECT_NAME}}

Modelo de ameaças, garantias de design e procedimento de resposta a incidentes. Complementa as decisões justificadas em [`PLAN.md`](./PLAN.md).

## Requisitos levantados na entrevista de bootstrap

{{SECURITY_REQUIREMENTS}}

## Modelo de ameaças (resumo)

<!-- Adapte conforme o tipo de projeto. Perguntas que ajudam a preencher esta seção:
     - Qual é o ponto central de confiança (servidor, banco de dados, provedor de identidade)?
     - O que acontece se ele for comprometido?
     - Que dados sensíveis o sistema guarda, e onde?
     - Quem são os atores com acesso privilegiado, e como esse acesso é revogado? -->

- {{THREAT_MODEL_NOTE_1}}
- {{THREAT_MODEL_NOTE_2}}

## Garantias de design

| Garantia | Como é implementada |
|---|---|
| Segredos nunca versionados | `.gitignore` + hook `.githooks/pre-commit` bloqueiam os casos mais óbvios |
| {{GUARANTEE_2}} | {{GUARANTEE_2_HOW}} |

## O que NÃO fazer (violação das garantias acima)

- Nunca fazer bind de serviços internos (banco de dados, painel administrativo) em `0.0.0.0` quando deveriam estar restritos a uma rede interna/VPN.
- Nunca commitar segredos (`.env` com credenciais reais, chaves privadas, tokens) no Git.
- Nunca desabilitar firewall/regras de rede em produção sem um plano de rollback imediato.
- {{SPECIFIC_DONT_1}}

## Hardening aplicado/planejado

Ver checklist completo em [`ROADMAP.md`](./ROADMAP.md) — Fase 5. Use a skill `security-baseline-audit` para revalidar periodicamente.

## Rotação e revogação de credenciais

<!-- Ex.: como revogar acesso de um usuário/dispositivo, como rotacionar chaves/segredos comprometidos. -->

- {{ROTATION_PROCEDURE_1}}

## Resposta a incidentes (procedimento de emergência)

Se houver suspeita real de comprometimento:

1. **Isolar**: cortar o acesso/tráfego suspeito (ex.: bloquear porta/rota específica) e revisar logs de acesso.
2. **Rotacionar credenciais**: qualquer segredo/token/chave que possa ter sido exposto.
3. **Auditar**: revisar logs de auditoria disponíveis e o histórico de mudanças recentes.
4. **Reconstruir se necessário**: preferir reprovisionar a "limpar" um ambiente comprometido, se a suspeita for séria.

## Reportando um problema de segurança

{{SECURITY_CONTACT_NOTE}}
