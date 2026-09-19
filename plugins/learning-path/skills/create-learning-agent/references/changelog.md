# Changelog de create-learning-agent

Cada versión trae tres bloques: **Cambios** (qué gana el repo generado), **Huellas** (cómo reconocer esa versión en un repo sin `state/agente.json`) y **Migración** (qué hace `/upgrade-agent` para llevar un repo de la versión anterior a esta). `/upgrade-agent` lo lee desde la skill entrante y aplica las migraciones en cadena, en orden, calculando el efecto neto (un archivo que una versión crea y otra posterior elimina nunca se crea).

**Regla de mantenimiento:** cualquier cambio a `assets/repo/` o a los protocolos del `CLAUDE.template.md` exige subir `metadata.version` en `SKILL.md` y añadir aquí la entrada correspondiente ANTES de empaquetar. Sin entrada en el changelog, los repos existentes no pueden actualizarse a esa versión.

**Vocabulario de las migraciones:** `crear` (el archivo no existe → copiar desde `assets/repo/`), `reemplazar` (existe → sobreescribir con la versión nueva, re-sustituyendo placeholders y re-aplicando personalizaciones), `eliminar`, `añadir clave` (solo si falta; el valor existente nunca se cambia). Las versiones anteriores a 3.0 están reconstruidas a partir de la historia de la skill: si un repo real no cuadra con una huella, gana lo que hay en el repo y el plan lo dice.

---

## 3.0 — 2026-09-09

**Cambios**
- Nuevo command `/upgrade-agent`: actualiza el motor del tutor a una versión nueva de la skill con plan previo, aprobación explícita y zona del estudiante intocable.
- Nuevo manifest `state/agente.json`: versión de la skill, placeholders con los que se generó el repo, personalizaciones y upgrades aplicados.
- `/config` registra cada personalización en el manifest (`personalizaciones[]`), para que los upgrades la preserven.
- Nueva carpeta `docs/upgrades/` con `_plantilla.md`: cada upgrade deja su plan y su resultado.
- `CLAUDE.md`: fila del manifest en "Archivos que gobiernan todo" y regla nueva en "Lo que NUNCA haces" (el motor solo cambia por `/config` o `/upgrade-agent`).
- `README.md`: fila de `/upgrade-agent`, estructura con `docs/upgrades/` y `state/agente.json`, sección "Actualizar el tutor".
- La skill queda versionada (`metadata.version` en `SKILL.md`) y trae `references/changelog.md`, `references/upgrade-protocol.md` y `scripts/validate_repo.py` (la validación del Paso 3 y la post-upgrade son el mismo script).

**Huellas**: existe `state/agente.json` con `skill: create-learning-agent` → la versión está en su campo `version`.

**Migración desde 2.2**
- `crear` `.claude/commands/upgrade-agent.md`, `docs/upgrades/_plantilla.md` (desde `plantilla-plan-upgrade.md`), `docs/upgrades/.gitkeep`.
- `crear` `state/agente.json` desde `agente.template.json`: `version` = la nueva, `generado_en` = fecha del primer commit del repo (`git log --reverse --format=%as | head -1`), `actualizado_en` = hoy, `placeholders` según el protocolo (recuperados del repo y confirmados en el plan), `personalizaciones` = las detectadas por diff y aprobadas, `upgrades` = la entrada de este upgrade.
- `reemplazar` `.claude/commands/config.md`, `CLAUDE.md`, `README.md`.
- `state/progress.json`: sin cambios de schema.

---

## 2.2 — 2026-08 (reconstruida)

**Cambios**
- `/break` y `/sesion` desaparecen; los sustituyen `/start-sesion` (abre y desarrolla la sesión) y `/end-sesion` (ceremonia de cierre explícita: estado, notas, commit, push). No existe pausa: `/end-sesion` se corre esté como esté la sesión.
- `state/progress.json` gana la clave `pendiente` (`null` o `{topic_id, ejercicio, paso, siguiente}`) para el trabajo a medias; `/start-sesion` lo retoma con un recap.
- Protocolos de `CLAUDE.md` y `README.md` reescritos alrededor de esos dos commands; `_reglas` de `progress.json` actualizadas.

**Huellas**: existe `.claude/commands/end-sesion.md` y no existe `state/agente.json`.

**Migración desde 2.1**
- `eliminar` `.claude/commands/break.md` y `.claude/commands/sesion.md`; `crear` `start-sesion.md` y `end-sesion.md`.
- `state/progress.json`: `añadir clave` `pendiente: null`; `reemplazar` `_reglas`.
- Si `/break` dejó contexto guardado (un archivo en `state/` distinto de `progress.json`, o una clave propia de pausa dentro de `progress.json`): conviértelo en `pendiente = {topic_id, ejercicio, paso, siguiente}` con lo que se pueda leer de él y elimina el archivo viejo. Es una excepción a "solo añadir": va explícita en el plan, con el contenido que se migra, y solo se aplica si el estudiante la aprueba.
- `reemplazar` `CLAUDE.md`, `README.md`, `.claude/commands/diagnostico.md`, `repaso.md`, `estado.md`, `fase.md`, `config.md`, `setup.md`.

---

## 2.1 — 2026-08 (reconstruida)

**Cambios**
- La teoría de cada tópico se entrega escrita en `ejercicios/fase-N/<topic_id>/leccion.md` (contenido exhaustivo + preguntas); en el chat el tutor solo pide leerla y discute las respuestas. Motivo: el chat de Claude Code no muestra bien contenido largo.
- Nueva plantilla `ejercicios/_plantilla/leccion.md`; `CLAUDE.md`, `README.md`, `ejercicios/README.md` y `/sesion` reescritos para ese flujo.

**Huellas**: existe `ejercicios/_plantilla/leccion.md` y existe `.claude/commands/break.md`.

**Migración desde 2.0**
- `crear` `ejercicios/_plantilla/leccion.md`.
- `reemplazar` `CLAUDE.md`, `README.md`, `ejercicios/README.md`, `.claude/commands/sesion.md` (efecto neto en cadena: `sesion.md` lo elimina 2.2, así que no se toca).

---

## 2.0 — 2026-08 (reconstruida)

**Cambios**
- Gate de `/setup`: el repo pide un remoto privado, prueba el push y guía el troubleshooting; sin `setup.estado == "completado"` no operan `/sesion` ni `/diagnostico`.
- 8 commands: `/setup`, `/sesion`, `/break`, `/diagnostico`, `/repaso`, `/estado`, `/fase`, `/config`.
- `state/progress.json` v2: bloques `setup` y `diagnostico` (con `nivel_global`, `niveles_por_fase`), `_reglas`.
- Código en inglés (identificadores, docstrings, comentarios); enunciados en español con paso a paso obligatorio (rutas, comandos, salida esperada).
- `material/` pasa a ser un vault de Obsidian: `.obsidian/` versionado (grafo coloreado por estado), una nota semilla por tópico en `material/fase-N/<Nombre>.md` con frontmatter espejo de `progress.json`, notas de sesión en `material/sesiones/` como hubs.
- Nuevas plantillas: `ejercicios/_plantilla/` (enunciado, starter, test), `material/sesiones/_plantilla.md`, `plantilla-nota-topico.md`; `.gitignore` con bloque del stack.

**Huellas**: existe `.claude/commands/setup.md` y no existe `ejercicios/_plantilla/leccion.md`.

**Migración desde 1.0**
- `crear` `.claude/commands/setup.md`, `fase.md`, `config.md` (`break.md` no se crea: 2.2 lo elimina).
- `state/progress.json`: `version` → `2` (schema, se reemplaza); bloque `diagnostico`: añadir `nivel_global: null`, `niveles_por_fase: {}`, `notas: []` si faltan (si `diagnostico` no existe como bloque, créalo con `estado: "pendiente"` salvo que el repo tenga tópicos con status, en cuyo caso `estado: "completado"` y `completado_en: null`); `añadir clave` `fortalezas: []`, `debilidades: []`, `sesiones_completadas` (= número de notas `material/sesiones/YYYY-MM-DD.md` si existen, si no 0), `ultima_sesion: null`; `reemplazar` `_reglas`. No se toca nada dentro de `topicos`.
- Bloque `setup` (excepción justificada: el gate bloquearía a un estudiante que ya viene usando el repo): si `git remote get-url origin` responde, `setup = {estado: "completado", remote: <url>, completado_en: <hoy>}`; si no hay remoto, `setup = {estado: "pendiente", remote: null, completado_en: null}` y el plan advierte que tras el upgrade deberá correr `/setup`.
- `crear` `material/.obsidian/app.json` y `graph.json`, `material/README.md`, `material/sesiones/_plantilla.md`, `ejercicios/_plantilla/enunciado.md`, `starter.py`, `test_starter.py`, `ejercicios/README.md`, `labs/README.md`, `.gitignore` (si ya existe: conserva al final las líneas que no estén en la plantilla).
- Semillas de tópico: por cada tópico de `roadmap/roadmap.yaml` sin nota en `material/fase-N/`, `crear` la semilla desde `plantilla-nota-topico.md` con `estado` y `nivel` leídos de `progress.json` (si el tópico ya tiene status) y los wikilinks de prerequisito según la regla del Paso 1.6 de SKILL.md. Si existe una nota del mismo tópico con otro nombre (mismo `topic_id` en frontmatter o título igual al nombre), no dupliques: añade el frontmatter que falte y déjala donde está; el plan lo lista.
- Frontmatter de notas existentes: `añadir clave` `topic_id`, `fase`, `tipo`, `estado`, `nivel`, `tags` si faltan (valores espejo de `progress.json`; `nivel: sin_evaluar` si no hay). El cuerpo no se toca.

---

## 1.0 — 2026-07 (reconstruida)

**Cambios**: primera versión del repo-tutor. `CLAUDE.md` con sesiones de ~30 min, estados `visto → aprendido → dominado`, repetición espaciada 2/7/21, diagnóstico y 4 commands: `/sesion`, `/diagnostico`, `/repaso`, `/estado`. `state/progress.json` sin bloque `setup`.

**Huellas**: no existe `.claude/commands/setup.md` (y `progress.json` no tiene bloque `setup`).

**Migración**: no aplica (versión inicial).
