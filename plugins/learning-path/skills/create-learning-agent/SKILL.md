---
name: create-learning-agent
description: Convierte un roadmap de estudio (.md) ya presente en la sesión en un repo-tutor completo en .zip para Claude Code, con CLAUDE.md pedagógico ("aquí se programa", explicación exhaustiva que asume cero conocimiento), roadmap.yaml, progreso versionado con git, vault de Obsidian (notas por tópico y por sesión, grafo por estado), ejercicios con paso a paso y código en inglés, lecciones por tópico, y slash commands (/setup, /diagnostico por preguntas puntuales, /start-sesion, /end-sesion, /repaso, /estado, /fase, /config y /upgrade-agent, que actualiza un repo-tutor ya generado a la versión nueva de esta skill sin tocar roadmap, progreso ni notas). Úsala SIEMPRE que el usuario invoque /learning-path:create-learning-agent (o /create-learning-agent), pida "crea el agente/tutor basado en el roadmap", "genera el repo del tutor" o "conviérteme este roadmap en un tutor" con un roadmap generado por generate-study-roadmap o presente en la conversación, y cuando pregunte cómo actualizar un repo-tutor. Es el paso 2 del flujo iniciado por generate-study-roadmap.
metadata:
  version: "3.0"
---

# Create Learning Agent

Toma un roadmap `.md` y produce `tutor-<slug>.zip`: un repo que se autoconfigura con `/setup` donde Claude Code actúa como tutor personal, con sesiones de ~30 minutos en las que **siempre se produce** (código o entregables verificables), estado que el propio tutor versiona con git, repetición espaciada, y un command `/upgrade-agent` con el que el repo se actualiza cuando esta skill cambia.

## Requisito de modelo

Esta skill está diseñada para el modelo más potente disponible (derivar un currículo estructurado y coherente es la parte difícil). Si estás corriendo en un modelo ligero (familia Haiku o equivalente), advierte al usuario ANTES de empezar y recomiéndale repetir con el modelo más capaz; continúa solo si lo confirma.

## Paso 0 — Localizar el roadmap

Busca en este orden: (1) el archivo que el usuario nombró, (2) archivos subidos o generados en esta conversación, (3) el roadmap producido por `generate-study-roadmap` en la sesión. Si no existe ninguno: pide al usuario correr `/learning-path:generate-study-roadmap` o subir su roadmap. **Nunca inventes un roadmap.**

Deriva del archivo: el **slug** (`ai-rust-roadmap.md` → `ai-rust`), el nombre del repo (`tutor-ai-rust`), el **tema** legible, y si el dominio es **programable** o no.

## Paso 1 — Construir el repo

Estructura obligatoria (idéntica al patrón de referencia):

```
tutor-<slug>/
├── CLAUDE.md
├── README.md
├── .gitignore
├── roadmap/roadmap.yaml
├── docs/roadmap.md            # copia del roadmap fuente
├── docs/upgrades/             # _plantilla.md + .gitkeep; aquí quedan los planes de /upgrade-agent
├── state/progress.json
├── state/agente.json          # manifest: versión de la skill, placeholders, personalizaciones
├── material/                  # vault de Obsidian
│   ├── README.md
│   ├── .obsidian/             # app.json, graph.json (config versionada)
│   ├── sesiones/_plantilla.md
│   └── fase-<n>/              # una nota semilla por tópico (ver Paso 1.6)
├── ejercicios/README.md
├── ejercicios/_plantilla/     # leccion.md, enunciado.md, starter.py, test_starter.py
├── ejercicios/diagnostico/.gitkeep
├── labs/README.md
└── .claude/commands/          # setup.md, start-sesion.md, end-sesion.md, diagnostico.md,
                               # repaso.md, estado.md, fase.md, config.md, upgrade-agent.md
```

Proceso:

1. Crea los directorios con `mkdir -p` y **rutas explícitas separadas** (el shell del entorno es `sh`: la brace expansion `{a,b}` NO funciona).
2. Copia TAL CUAL desde `assets/repo/` los archivos independientes del dominio — no los regeneres de memoria (introduce drift): `commands/*` → `.claude/commands/`, `progress.json` → `state/`, `plantilla-ejercicio/*` → `ejercicios/_plantilla/`, `ejercicios-README.md`, `material-README.md`, `obsidian/*` → `material/.obsidian/`, `plantilla-nota-sesion.md` → `material/sesiones/_plantilla.md`, `plantilla-plan-upgrade.md` → `docs/upgrades/_plantilla.md` (más `docs/upgrades/.gitkeep`).
3. Genera desde plantillas, sustituyendo los placeholders `{{...}}`: `CLAUDE.template.md` → `CLAUDE.md`, `README.template.md` → `README.md`, `labs-README.template.md` → `labs/README.md`, `gitignore.template` → `.gitignore`. Placeholders: `{{TEMA}}`, `{{SLUG}}`, `{{N_FASES}}`, `{{N_TOPICOS}}`, `{{HERRAMIENTAS_EVAL}}` (comandos con los que el tutor evalúa, p. ej. `pytest`, `cargo test`), `{{EJEMPLO_TEST}}` (framework de tests del dominio), `{{LABS_EJEMPLOS}}` (infra típica del tema), `{{REQUISITOS_EXTRA}}` (toolchain a instalar), `{{STACK_GITIGNORE}}` (líneas de ignore propias del stack). Verifica al final que no quede ningún `{{` sin sustituir.
4. Genera `state/agente.json` desde `agente.template.json` con los MISMOS valores que usaste en el punto anterior: `{{VERSION}}` = `metadata.version` del frontmatter de este SKILL.md, `{{FECHA}}` = hoy, y cada placeholder de dominio tal cual se sustituyó. Instáncialo con `json` (carga la plantilla, asigna los valores, `json.dump(..., indent=2, ensure_ascii=False)`), NO por sustitución de texto: `STACK_GITIGNORE` es multilínea y un salto de línea literal dentro de un string rompe el JSON. Este manifest es lo que permite que `/upgrade-agent` regenere `CLAUDE.md`, `README.md` y `.gitignore` con una versión futura de la skill sin volver a adivinar el dominio; un valor vacío aquí es un upgrade roto después.
5. Genera `roadmap/roadmap.yaml` derivándolo del `.md`: **lee antes `references/roadmap-yaml-spec.md`** y sigue ese schema al pie de la letra (IDs `f<n>.<slug>`, tipos `codigo|mixto|conceptual`, criterio de dominio por tópico y por fase, capstone por fase).
6. Copia el roadmap fuente a `docs/roadmap.md`.
7. Genera las **notas semilla de Obsidian**: una por tópico del `roadmap.yaml`, en `material/fase-<n>/<Nombre del tópico>.md`, instanciando `assets/repo/plantilla-nota-topico.md`. Reglas:
   - **Nombre de archivo = `nombre` del tópico en el yaml** (es la etiqueta del nodo en el grafo y el destino de los wikilinks). Sanitiza solo los caracteres que Obsidian/OS no aceptan en filenames (`/ \ : * ? " < > | # ^ [ ]`), conservando tildes y espacios.
   - Placeholders: `{{TOPIC_ID}}`, `{{FASE_N}}`, `{{TIPO}}`, `{{TOPIC_NOMBRE}}`, `{{CRITERIO_DOMINIO}}` salen directo del yaml. `{{PREREQUISITOS_WIKILINKS}}` = wikilinks `[[Nombre]]` al **tópico anterior en el orden secuencial** (el previo de su fase; para el primero de una fase, el último de la fase anterior) más los `prerequisitos:` explícitos del yaml, resueltos de id a nombre. El primer tópico de f1 lleva `ninguno`.
   - Las semillas NO llevan más links que esos: los links semánticos los añade el tutor en sesión según la regla de links del CLAUDE.md.

## Paso 2 — Adaptar al dominio

- **Dominio programable** (lenguajes, data, infra...): la regla "aquí se programa" queda intacta; solo ajusta comandos de evaluación y ejemplos de labs a las herramientas del roadmap.
- **Dominio no programable** (idiomas, música, finanzas...): transforma la regla en "aquí se produce": cada sesión exige un entregable concreto y verificable; los tipos de ejercicio se adaptan (`producir`, `completar`, `corregir`, `predecir`) y la evaluación es revisión objetiva contra criterios explícitos escritos en el enunciado.
- **No cambies nunca**: el protocolo de sesión de 30 min con apertura en `/start-sesion` y cierre SOLO en `/end-sesion` (no existe `/break` ni pausa: `progress.json.pendiente` guarda el trabajo a medias), los estados y su progresión (`no_visto → visto → aprendido → dominado`), la repetición espaciada (2/7/21 días), `dominado` solo en sesión posterior, las pistas escalonadas con penalización, el diagnóstico por preguntas puntuales (nunca autoevaluación genérica) con su tabla de niveles `nulo/bajo/medio/alto/experto` y su regla conservadora (sin ejercicio verificado nadie pasa de `medio`), el cierre con actualización de estado + commit + push, el gate de `/setup` (sin remoto configurado no operan `/start-sesion` ni `/diagnostico`), el estándar código-en-inglés/enunciados-en-español, el paso a paso obligatorio en los enunciados, la entrega de la teoría escrita en la `leccion.md` de cada tópico (nunca dictada en el chat), la **regla de explicación exhaustiva** del CLAUDE.md (asumir cero conocimiento, definir cada término, explicar cada línea y cada comando, no saltar pasos — la lección puede ser larga; el chat no), ni el gate de `/upgrade-agent` (plan escrito antes de tocar nada, aplicación solo con `aprobado`, zona del estudiante intocable). En dominios no programables, "código en inglés" se relaja a: los artefactos siguen la convención de nombres estándar del dominio.

## Paso 3 — Validar (obligatorio antes de empaquetar)

Ejecuta el validador que trae esta skill (misma carpeta que este SKILL.md; si falta pyyaml: `pip install pyyaml --break-system-packages`):

```bash
python3 <ruta-de-esta-skill>/scripts/validate_repo.py tutor-<slug> --fresh
```

Comprueba `state/progress.json` (bloque `setup` en `pendiente`, clave `pendiente`, `diagnostico` con `nivel_global` y `niveles_por_fase`), `roadmap/roadmap.yaml` contra el schema (IDs únicos, `tipo` válido, `criterio_dominio`, suma de horas = `meta.horas_totales_estimadas`), los 9 commands, `state/agente.json` (versión = la de este SKILL.md y ningún placeholder vacío), una nota semilla por tópico con `topic_id` coincidente, wikilinks de prerequisito resolubles, y que no quede ningún `{{PLACEHOLDER}}` sin sustituir. Si algo falla, corrígelo y revalida hasta ver `0 errores`. El mismo script, con `--diff-base HEAD`, es el que `/upgrade-agent` corre después de actualizar un repo.

## Paso 4 — Empaquetar y entregar

```bash
cd <directorio padre> && zip -rq /mnt/user-data/outputs/tutor-<slug>.zip tutor-<slug>
```

Presenta el zip con `present_files` y cierra breve: qué contiene (3-5 líneas, destacando cómo quedó adaptada la regla de producción al dominio) + el bloque de arranque:

```bash
unzip tutor-<slug>.zip && cd tutor-<slug>
claude
> /setup        # inicializa git, conecta tu repo privado y valida el push
> /diagnostico  # cuando /setup confirme la configuración
> /start-sesion # cada sesión de estudio...
> /end-sesion   # ...y su cierre explícito (estado + commit + push)
```

## Actualizar un repo ya generado

Los repos no heredan los cambios de esta skill: se actualizan con su propio command `/upgrade-agent`, que toma el `.skill` nuevo y sigue `references/upgrade-protocol.md` y `references/changelog.md` de la skill entrante. Si el usuario pregunta cómo actualizar su tutor, el flujo es:

1. Descargar esta skill desde claude.ai como `.skill` y dejarla donde el tutor la vea (p. ej. `~/Downloads`).
2. En el repo: `claude`, entrar en plan mode (Shift+Tab, recomendado) y `/upgrade-agent ~/Downloads`.
3. Revisar el plan en `docs/upgrades/<fecha>-v<actual>-a-v<nueva>.md` y responder `aprobado` (o pedir cambios).

Se actualiza el motor (commands, `CLAUDE.md`, plantillas, comportamientos) conservando las personalizaciones de `/config`; el roadmap, el progreso, las notas y los ejercicios no se tocan. **Repos anteriores a 3.0** (sin `/upgrade-agent`): copiar `assets/repo/commands/upgrade-agent.md` de esta skill a `.claude/commands/` del repo y ejecutarlo (el command tolera que ese único archivo esté sin commit; lo commitea con el upgrade y lo deja en su versión definitiva). No hace falta leer el protocolo para generar un repo nuevo: solo lo usa el command.

## Versionado y mantenimiento de esta skill

La versión vive en `metadata.version` del frontmatter. **Cada cambio a `assets/repo/` o a los protocolos del `CLAUDE.template.md` exige subir esa versión y añadir la entrada correspondiente en `references/changelog.md`** (cambios, huellas para reconocer la versión en un repo sin manifest, y migración desde la anterior) ANTES de empaquetar. Sin entrada en el changelog, `/upgrade-agent` no puede llevar los repos existentes a la versión nueva: el changelog es la migración. Si el cambio toca `scripts/validate_repo.py` (nuevos archivos obligatorios, nuevas claves), la migración correspondiente debe crearlos, o los repos actualizados fallarán la validación.

## Errores a evitar

- Regenerar "de memoria" los archivos que `assets/repo/` trae listos.
- Tópicos sin `criterio_dominio` o con criterios no verificables.
- Empaquetar sin correr la validación del Paso 3.
- Inventar contenido: si una sección del roadmap no da para derivar tópicos, pregunta al usuario en lugar de rellenar.
- Dejar placeholders `{{...}}` sin sustituir en los archivos finales — incluido `state/agente.json`.
- Generar código (plantillas, esqueletos, tests) con identificadores, docstrings o comentarios en español: el código va en inglés; en español van los enunciados y la conversación.
- Notas semilla con links inventados: solo el anterior secuencial + `prerequisitos:` del yaml.
- Nombrar las notas de tópico con el `topic_id` en vez del nombre legible (el grafo mostraría `f1.slug` como etiqueta).
- Debilitar el diagnóstico al adaptar el CLAUDE.md: reintroducir autoevaluación ("¿sabes alto/medio/bajo?"), quitar la tabla de niveles o permitir `alto`/`experto` sin ejercicio verificado.
- Recortar o "resumir" la regla de explicación exhaustiva al adaptar el CLAUDE.md al dominio: el tutor generado debe explicar siempre como si el estudiante no supiera nada.
- Publicar una versión nueva de la skill sin subir `metadata.version` ni escribir su entrada (huellas + migración) en `references/changelog.md`.
