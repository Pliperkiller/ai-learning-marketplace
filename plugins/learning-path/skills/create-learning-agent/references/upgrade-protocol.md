# Protocolo de /upgrade-agent

Lo lee el command `/upgrade-agent` de un repo-tutor **desde la skill nueva ya descomprimida**. Este documento manda sobre lo que el command sepa de sí mismo: el repo puede tener un command viejo, pero cómo se migra lo sabe la versión entrante. Los invariantes del command (zona del estudiante intocable, plan antes de tocar nada, commit solo tras validar) no se negocian aquí ni en ninguna versión futura.

Vocabulario: `repo` = el repo-tutor donde corre el command; `skill` = carpeta descomprimida de la skill nueva; `V_actual` / `V_nueva`; `manifest` = `state/agente.json`.

## 1. Zonas del repo

| Zona | Archivos | Regla |
|---|---|---|
| **Motor** (lo gobierna la skill) | `CLAUDE.md`, `README.md`, `.gitignore`, `.claude/commands/*` que vengan de la skill, `ejercicios/_plantilla/*`, `ejercicios/README.md`, `material/README.md`, `labs/README.md`, `material/.obsidian/*`, `material/sesiones/_plantilla.md`, `docs/upgrades/_plantilla.md`, `state/agente.json` | Crear / reemplazar / eliminar según el changelog, re-sustituyendo placeholders y re-aplicando personalizaciones. |
| **Estudiante** (intocable) | `roadmap/roadmap.yaml`, `docs/roadmap.md`, los valores de `state/progress.json`, `material/fase-*/*.md`, `material/sesiones/YYYY-MM-DD.md`, `ejercicios/fase-*/**`, `ejercicios/diagnostico/**`, `labs/<nombre>/**`, `docs/upgrades/*.md` anteriores, y cualquier command de `.claude/commands/` que no venga de la skill | No se modifica ni se borra. Nunca. |
| **Híbrida** (migración aditiva) | Schema de `state/progress.json`, frontmatter de las notas de tópico, estructura que falte (directorios, semillas de tópico sin nota, plantillas) | Solo se añaden claves o archivos que falten, con su valor por defecto. Un valor existente no se cambia; un archivo existente no se sobreescribe. Las únicas excepciones son las que el changelog declara como tales, y van escritas en el plan antes de la aprobación. |

`.gitignore` es motor, pero el estudiante suele añadirle líneas: se regenera desde la plantilla y se conservan al final, bajo `# Personalizado`, las líneas actuales que no estén en la plantilla nueva.

## 2. Determinar V_actual

1. Si existe `state/agente.json` y `skill == "create-learning-agent"`: `V_actual = version`. Punto.
2. Si no existe: recorre las **Huellas** de `references/changelog.md` de la versión más reciente a la más antigua; la primera que cuadre es `V_actual`. Regístrala en el plan como **supuesta**, con las huellas que la sostienen, y pide confirmación en el resumen del chat. Si dos huellas se contradicen (p. ej. hay `end-sesion.md` pero no `progress.json.pendiente`), toma la versión más antigua compatible y aplica de más: las migraciones son idempotentes (crear lo que ya existe no hace nada; añadir una clave que ya está no la cambia).

## 3. Construir el plan (sin escribir en el repo)

### 3.1 Cadena de versiones
Toma todas las entradas del changelog con versión > `V_actual` y ≤ `V_nueva`, de la más antigua a la más nueva. La lista de acciones es la unión de sus migraciones con efecto neto: si una versión crea un archivo y una posterior lo elimina, no se crea; si varias reemplazan el mismo archivo, se reemplaza una vez con la versión final (la de `assets/repo/` de la skill).

### 3.2 Placeholders
Los archivos generados desde plantilla (`CLAUDE.md`, `README.md`, `.gitignore`, `labs/README.md`) llevan `{{TEMA}}`, `{{SLUG}}`, `{{N_FASES}}`, `{{N_TOPICOS}}`, `{{HERRAMIENTAS_EVAL}}`, `{{EJEMPLO_TEST}}`, `{{LABS_EJEMPLOS}}`, `{{REQUISITOS_EXTRA}}`, `{{STACK_GITIGNORE}}`. Para reemplazarlos hay que volver a sustituirlos:
- Con manifest: usa `placeholders` tal cual. `N_FASES` y `N_TOPICOS` se recalculan siempre de `roadmap/roadmap.yaml`.
- Sin manifest: infiérelos del repo actual y márcalos en el plan con su origen:

| Placeholder | De dónde sale en el repo actual |
|---|---|
| `TEMA` | Título de `CLAUDE.md` (`# Tutor de <TEMA>`) |
| `SLUG` | Nombre de la carpeta del repo (`tutor-<slug>`) o el `unzip tutor-<slug>.zip` del `README.md` |
| `HERRAMIENTAS_EVAL` | `CLAUDE.md`, regla "Evalúas EJECUTANDO y leyendo su trabajo (<aquí>)" |
| `EJEMPLO_TEST` | `CLAUDE.md`, tipo de ejercicio `test`: "verificación que falla (<aquí>)" |
| `LABS_EJEMPLOS` | `CLAUDE.md`, sección "Labs": "infraestructura local (<aquí>)" |
| `REQUISITOS_EXTRA` | `README.md`, sección "Requisitos", la viñeta que no es Git ni Claude Code |
| `STACK_GITIGNORE` | `.gitignore`, todo lo que sigue a `# Stack del tema` |

Si alguno no aparece (el archivo fue muy personalizado o la versión no lo tenía), propón un valor a partir de `tecnologias` del yaml y márcalo como **propuesto**: el estudiante lo confirma o lo corrige antes de aprobar.

### 3.3 Inventario del motor
Usa el mismo mapa origen → destino del Paso 1 de `SKILL.md` (`commands/*` → `.claude/commands/`, `progress.json` → `state/`, `plantilla-ejercicio/*` → `ejercicios/_plantilla/`, `ejercicios-README.md` → `ejercicios/README.md`, `material-README.md` → `material/README.md`, `obsidian/*` → `material/.obsidian/`, `plantilla-nota-sesion.md` → `material/sesiones/_plantilla.md`, `plantilla-plan-upgrade.md` → `docs/upgrades/_plantilla.md`, y las cuatro plantillas `*.template.*`). Para cada destino decide: `crear` (no existe), `reemplazar` (existe y el contenido difiere de lo que produciría la plantilla nueva), `igual` (no se lista), `eliminar` (lo dicta el changelog). Los commands presentes en el repo que ni vienen de la skill ni figuran como eliminados en el changelog son del estudiante: `conservar`, y se listan para que lo sepa.

`assets/repo/progress.json` y `plantilla-nota-topico.md` NO son destinos de reemplazo: son la fuente de los valores por defecto para las migraciones aditivas (3.5). `state/agente.json` tampoco se copia ni se reemplaza nunca (perdería las personalizaciones): se crea o actualiza campo a campo en el paso 4.5.

### 3.4 Personalizaciones
Un upgrade que borra un ajuste que el estudiante pidió con `/config` es peor que no actualizar. Dos fuentes:
1. **Manifest** (`personalizaciones[]`): cada entrada se **re-aplica sobre la versión nueva del archivo** ("rebase" del ajuste, no merge de texto): localiza en la plantilla nueva la sección o regla que describe `detalle` y aplica el mismo cambio. Si esa sección ya no existe o la versión nueva la reescribió con otra lógica (p. ej. el ajuste tocaba `/break` y `/break` desapareció), márcala como **conflicto** en el plan: explica por qué y propón qué hacer; el estudiante decide.
2. **Sin manifest o para ajustes no registrados**: diff semántico del archivo actual contra la plantilla nueva instanciada. Son candidatas a personalización las secciones, reglas, filas de tabla o frases que están en el archivo actual, no están en la plantilla nueva y no figuran en el changelog como eliminadas o reescritas. Cada candidata va al plan como hipótesis con decisión propuesta (`conservar` por defecto); el estudiante confirma o descarta. Lo que se confirme se registra en el manifest nuevo con `detalle` preciso, para que el siguiente upgrade ya no tenga que adivinar.

Los commands propios del estudiante no se tocan (zona estudiante). Si uno de ellos referencia algo que la versión nueva elimina (p. ej. invoca `/break`), avísalo en el plan sin modificarlo.

### 3.5 Migraciones aditivas
- **`state/progress.json`**: compara con `assets/repo/progress.json` de la skill. Toda clave de nivel superior o dentro de `setup` / `diagnostico` que falte se añade con el valor por defecto del asset. `_reglas` y `version` (versión del schema del archivo) se reemplazan por los del asset: son metadatos del motor, no datos. Nada dentro de `topicos`, `posicion_actual`, `pendiente`, `fortalezas`, `debilidades`, `sesiones_completadas`, `ultima_sesion` ni en los valores existentes de `setup` y `diagnostico` se cambia. Las excepciones (p. ej. contexto de `/break` → `pendiente`, o `setup` derivado del remoto) solo existen si el changelog las declara, y van en el plan con el valor concreto que se escribirá.
- **Frontmatter de notas de tópico** (`material/fase-*/*.md`): añade las claves que falten según `plantilla-nota-topico.md` (`topic_id`, `fase`, `tipo`, `estado`, `nivel`, `tags`), con valores espejo de `progress.json` (`estado` = status del tópico o `no_visto`; `nivel` = nivel del tópico o `sin_evaluar`). Claves existentes y cuerpo de la nota: sin cambios, aunque estén desincronizados — eso lo corrige el tutor en el siguiente `/end-sesion`, donde `progress.json` manda.
- **Semillas faltantes**: por cada tópico del yaml sin nota en `material/fase-N/` (busca por `topic_id` en frontmatter y por nombre de archivo), crea la semilla con la regla del Paso 1.6 de `SKILL.md`. Si hay una nota del mismo tópico con otro nombre, no dupliques: completa su frontmatter y lístalo.
- **Estructura**: directorios y `.gitkeep` que falten (`docs/upgrades/`, `ejercicios/diagnostico/`, `labs/`), plantillas que no existían en la versión actual.

### 3.6 Escribir el plan
Instancia `docs/upgrades/_plantilla.md` (o `assets/repo/plantilla-plan-upgrade.md` de la skill si el repo aún no la tiene) en `docs/upgrades/YYYY-MM-DD-v<actual>-a-v<nueva>.md`, con todas las secciones llenas: nada de "varios archivos" — cada archivo con su acción y su motivo, cada personalización con su decisión, cada clave que se añade con su valor. La sección "Lo que NO se toca" se escribe completa aunque parezca repetitiva: es lo que el estudiante mira primero. En el chat: resumen (versiones, cuántos archivos por acción, personalizaciones y supuestos a confirmar) + la ruta del plan + "responde `aprobado` o dime qué cambiar". Si el entorno impide escribir (plan mode), el plan se presenta por el mecanismo de plan y el archivo se escribe al empezar la fase 2.

## 4. Aplicación (solo tras `aprobado`)

Orden fijo; cada paso deja el repo en un estado que el siguiente puede verificar:
1. Si el archivo del plan no existe aún (plan mode), escríbelo ahora con estado `aprobado`.
2. **Motor**: ejecuta las acciones de 3.3 con un script (no a mano archivo por archivo): copia desde `assets/repo/` los archivos independientes del dominio; instancia las plantillas sustituyendo placeholders (verifica `{{[A-Z_]+}}` = 0 en el resultado); elimina lo que el changelog elimina; regenera `.gitignore` conservando las líneas propias.
3. **Migraciones aditivas** de 3.5, también por script: carga JSON/YAML, añade solo lo que falta, vuelca con `indent=2, ensure_ascii=False` (JSON) o conservando el texto original y editando solo el bloque de frontmatter (notas: nunca re-serialices el cuerpo).
4. **Personalizaciones**: re-aplica las decididas en 3.4 sobre los archivos ya regenerados.
5. **Manifest**: crea o actualiza `state/agente.json` con `json` (nunca por sustitución de texto: `STACK_GITIGNORE` es multilínea): `version = V_nueva`, `actualizado_en = hoy`, `placeholders` definitivos, `personalizaciones` (las del manifest anterior + las confirmadas por diff), y añade a `upgrades` `{fecha, de: V_actual, a: V_nueva, plan: <ruta del plan>}`. Al crearlo por primera vez, `generado_en` = fecha del primer commit del repo.
6. **Validación**: `python3 <skill>/scripts/validate_repo.py . --diff-base HEAD`. El script comprueba el schema completo del repo en la versión nueva (commands, manifest, `progress.json`, yaml, semillas, placeholders) y que la zona del estudiante no cambió respecto a `HEAD`: cero modificaciones o borrados en sus archivos, y en `progress.json` y en las notas solo adiciones. Si falla, corrige y repite; si no puedes dejarlo en verde, `git checkout -- . && git clean -fd` para volver a `HEAD`, deja el plan con estado `fallido` y el motivo, y díselo al estudiante. Nunca commitees en rojo.
7. **Resultado**: en el archivo del plan, estado `aplicado` y la sección "Resultado" con fecha, salida resumida de la validación, e incidencias.
8. **Git**: `git add -A && git commit -m "upgrade: agente v<actual> → v<nueva>"`, `git tag agente-v<nueva>` (si el tag existe, no lo muevas: dilo), `git push && git push --tags`. Si el push falla, muéstralo y no des el upgrade por cerrado.
9. Borra el directorio temporal de la skill. Cierra con: versión nueva, commands nuevos o eliminados, qué debe hacer distinto el estudiante en su próxima sesión, y cómo revertir (`git revert <commit>`).

## 5. Casos borde

- **Misma versión**: nada que actualizar. Si el estudiante sospecha que el motor está corrupto o desalineado, ofrece un "reparar": mismo protocolo, misma versión, que solo produce acciones `reemplazar` para archivos del motor que difieran; el plan lo dice explícitamente y se registra en `upgrades` con `de == a`.
- **Downgrade**: no se soporta; pide la skill más reciente.
- **Árbol sucio**: se detiene antes de todo. No hay excepciones: un upgrade sobre cambios sin commit no se puede revertir limpiamente.
- **La skill no es `create-learning-agent`** o no tiene `references/upgrade-protocol.md`: detente y dilo (una skill sin protocolo es anterior a 3.0: no puede ser más nueva que un repo que ya tiene `/upgrade-agent`).
- **Varias candidatas** en la carpeta indicada: la más reciente por fecha de modificación, diciendo cuál se eligió y cuáles se descartaron.
- **Falta pyyaml**: `pip install pyyaml` (con `--break-system-packages` si el pip lo exige). El script de validación lo necesita.
- **Upgrade interrumpido** (el estudiante cerró Claude a mitad de la fase 2): al re-ejecutar, `git status` sucio detiene el command; el estudiante decide entre `git checkout -- . && git clean -fd` (volver a `HEAD` y repetir) o revisar lo que quedó. No intentes "continuar donde iba".
- **Plan rechazado**: elimina el archivo del plan sin commit, limpia el temporal, y anota en el chat qué objeción tuvo por si quiere retomarlo.
- **Repo sin manifest y sin huella clara** (estructura muy personalizada): trata `V_actual` como la más antigua que tenga sentido, lista en el plan cada supuesto, y deja que el estudiante corrija antes de aprobar. Aplicar de más es seguro; aplicar de menos deja el tutor roto.
