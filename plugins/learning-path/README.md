# learning-path

Plugin de Claude Code con dos skills encadenadas que convierten *"quiero aprender X"* en un tutor de IA funcionando.

```
/learning-path:generate-study-roadmap  →  roadmap-<tema>.md
            ↓ (refínalo en la conversación)
/learning-path:create-learning-agent   →  tutor-<tema>.zip
            ↓ (descomprime, abre con Claude Code)
/setup → /diagnostico → /start-sesion → ...
```

## Skills

### `generate-study-roadmap`

Investiga el tema en la web y produce un roadmap de estudio en `.md`: fases secuenciales, criterios de dominio que se puedan demostrar (no listas de herramientas), y un capstone que evoluciona fase a fase.

Es **estándar y desde cero** a propósito: no se personaliza a tu historial. La ubicación de tu nivel real la hace después el tutor con su `/diagnostico`.

Dispara con `/learning-path:generate-study-roadmap <tema>`, o con frases como *"un roadmap para aprender X"*, *"ruta de estudio de X"*, *"quiero aprender X"*.

### `create-learning-agent`

Toma ese `.md` y genera `tutor-<slug>.zip`, un repo donde Claude Code actúa como tutor:

- `CLAUDE.md` pedagógico — explica asumiendo cero conocimiento, y en cada sesión **se produce** algo verificable.
- `roadmap/roadmap.yaml` — el currículo en estructura consultable.
- `state/progress.json` versionado con git por el propio tutor.
- Ejercicios con enunciado, lección, starter y tests. Código en inglés.
- Vault de Obsidian: una nota por tópico y por sesión, con grafo coloreado por estado.
- 9 slash commands: `/setup`, `/diagnostico`, `/start-sesion`, `/end-sesion`, `/repaso`, `/estado`, `/fase`, `/config`, `/upgrade-agent`.

Valida el repo generado antes de empaquetar (`scripts/validate_repo.py`) y no entrega si quedan errores.

Dispara con `/learning-path:create-learning-agent` teniendo el roadmap en la sesión, o con *"conviérteme este roadmap en un tutor"*.

## Requisito de modelo

Ambas skills están diseñadas para el modelo más potente disponible: investigar un campo y diseñar un currículo coherente son la parte difícil, y con un modelo ligero la calidad cae. Elige el modelo antes de invocarlas.

## Versiones

`version` en `.claude-plugin/plugin.json` es la del plugin. La del motor del repo-tutor vive aparte, en `metadata.version` del `SKILL.md` de `create-learning-agent`, porque es la que usa `/upgrade-agent` para migrar repos ya generados. Al tocar `assets/repo/`, sube esa versión y escribe la entrada en `references/changelog.md`.
