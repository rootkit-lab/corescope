Execute agora a entrevista de bootstrap da skill `project-bootstrap` (ver `.cursor/skills/project-bootstrap/SKILL.md`), independentemente do que `.cursor/state/bootstrap.json` disser.

Se `status` já for `"done"` (ou já existir `PLAN.md`/`ROADMAP.md`/`SECURITY.md` preenchidos na raiz), avise explicitamente o usuário que isto vai **refazer o bootstrap** e pode sobrescrever esses documentos — peça confirmação antes de continuar. Se ele confirmar, siga o roteiro completo da skill do zero (entrevista → geração de docs → stack → dev → deploy → git) e ao final atualize `.cursor/state/bootstrap.json` novamente.

Se o usuário passou texto extra depois do comando (ex.: `/start-project um SaaS de agendamento em Node/TS`), use isso como resposta já dada para a(s) primeira(s) pergunta(s) da entrevista (nome/descrição do projeto), mas ainda confirme os demais pontos (tipo, stack, deploy, escala, segurança) antes de gerar qualquer arquivo.
