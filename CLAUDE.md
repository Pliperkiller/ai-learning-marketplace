# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code **plugin marketplace** (`pliperkiller-learning`) with one plugin, `learning-path`, containing two chained skills written in Spanish:

1. `generate-study-roadmap` — researches a topic on the web and writes `<slug>-roadmap.md` (6-9 phases, verifiable mastery criteria, evolving capstone).
2. `create-learning-agent` — turns that roadmap into `tutor-<slug>.zip`, a self-contained repo where Claude Code acts as a personal tutor (30-min sessions, exercises with tests, git-versioned progress, Obsidian vault, 9 slash commands).

There is no application code to build or run here. The "product" is Markdown skill instructions, templates, and one Python validator. Prose (skills, templates, READMEs, chat) is in **Spanish**; code inside templates (identifiers, docstrings, comments) is in **English**. Keep that split.

## Commands

```bash
# Validate marketplace + plugin manifests (run before pushing)
claude plugin validate .

# Validate a generated tutor repo (needs pyyaml). --fresh = just generated.
python3 plugins/learning-path/skills/create-learning-agent/scripts/validate_repo.py <tutor-dir> --fresh
# Post-upgrade check: fail if any student-zone file changed vs HEAD
python3 plugins/learning-path/skills/create-learning-agent/scripts/validate_repo.py <tutor-dir> --diff-base HEAD
```

Local install for testing, from a Claude Code session (loads in place, so `SKILL.md` edits show up without reinstalling; `/reload-plugins` may be needed):

```
/plugin marketplace add ./ai-learning-marketplace
/plugin install learning-path@pliperkiller-learning
```

There is no test suite. `validate_repo.py` exits 1 on errors, 0 with warnings; it reads the expected engine version from the `SKILL.md` two levels above it (`scripts/../SKILL.md`), so do not move the script.

## Layout

```
.claude-plugin/marketplace.json                # catalog; plugin entry carries its own version
plugins/learning-path/
  .claude-plugin/plugin.json                   # plugin version
  skills/generate-study-roadmap/
    SKILL.md, assets/plantilla-roadmap.md      # step 1
  skills/create-learning-agent/
    SKILL.md                                   # step 2; metadata.version = tutor ENGINE version
    assets/repo/                               # everything copied/instantiated into a tutor repo
    references/roadmap-yaml-spec.md            # schema roadmap.yaml must follow
    references/changelog.md                    # per-version Cambios / Huellas / Migración
    references/upgrade-protocol.md             # what /upgrade-agent does inside a tutor repo
    scripts/validate_repo.py
```

Skills under `plugins/learning-path/skills/<name>/SKILL.md` are auto-discovered; nothing declares them. A skill cannot reference files outside its own directory (`../`) because install copies only the plugin dir.

## Three independent versions

This is the easiest thing to get wrong:

| Version | Where | Bump when |
|---|---|---|
| Plugin | `plugins/learning-path/.claude-plugin/plugin.json` **and** the plugin entry in `marketplace.json` (keep in sync) | Any published change; otherwise users keep the cached copy |
| Tutor engine | `metadata.version` in `create-learning-agent/SKILL.md` | Any change to `assets/repo/` or to protocols in `CLAUDE.template.md` |
| progress schema | `version` inside `assets/repo/progress.json` | Schema change to the student's progress file |

An engine bump **requires** a new entry in `references/changelog.md` with the three blocks (Cambios, Huellas, Migración desde la anterior). Generated tutor repos do not inherit skill changes; their `/upgrade-agent` command reads the incoming skill's changelog and applies migrations in chain. No changelog entry means existing repos cannot be upgraded. If a change adds required files or keys to `validate_repo.py`, the migration must create them or upgraded repos will fail validation.

## How the tutor repo is assembled (create-learning-agent)

`assets/repo/` maps onto the generated repo as follows. `/upgrade-agent` uses the same map, so changing a destination path here means changing the protocol and validator too.

- Copied verbatim: `commands/*` → `.claude/commands/`, `progress.json` → `state/`, `plantilla-ejercicio/*` → `ejercicios/_plantilla/`, `ejercicios-README.md`, `material-README.md`, `obsidian/*` → `material/.obsidian/`, `plantilla-nota-sesion.md` → `material/sesiones/_plantilla.md`, `plantilla-plan-upgrade.md` → `docs/upgrades/_plantilla.md`.
- Instantiated from `{{PLACEHOLDER}}` templates: `CLAUDE.template.md`, `README.template.md`, `labs-README.template.md`, `gitignore.template`, `agente.template.json` (the manifest; built with `json.dump`, not text substitution, because `STACK_GITIGNORE` is multiline), `plantilla-nota-topico.md` (one seed note per topic, filename = topic `nombre`, not `topic_id`).
- Derived: `roadmap/roadmap.yaml` from the `.md` per `roadmap-yaml-spec.md` (IDs `f<n>.<slug>`, `tipo` in `codigo|mixto|conceptual`, `criterio_dominio` per topic, hours sum must equal `meta.horas_totales_estimadas`).

Domain placeholders: `TEMA`, `SLUG`, `N_FASES`, `N_TOPICOS`, `HERRAMIENTAS_EVAL`, `EJEMPLO_TEST`, `LABS_EJEMPLOS`, `REQUISITOS_EXTRA`, `STACK_GITIGNORE`. Adding one means updating `agente.template.json`, `PLACEHOLDER_KEYS` in the validator, and the placeholder-recovery table in `upgrade-protocol.md`.

The upgrade protocol divides a tutor repo into zones: **motor** (skill-owned, replaceable), **estudiante** (roadmap, progress values, notes, exercises, labs, student-written commands: never touched), **híbrida** (progress schema and note frontmatter: additive only). `STUDENT_ZONE` / `HYBRID` in `validate_repo.py` encode this; keep them consistent with the protocol table.

## Invariants baked into the templates

`create-learning-agent/SKILL.md` "Paso 2" lists behaviors the generated tutor must never lose when adapting to a domain. Editing `CLAUDE.template.md` or the commands should preserve them: session open only via `/start-sesion` and close only via `/end-sesion` (no pause command; half-done work lives in `progress.json.pendiente`), state progression `no_visto → visto → aprendido → dominado` with spaced repetition at 2/7/21 days, diagnosis by concrete questions (never self-assessment) with the conservative rule that nobody exceeds `medio` without a verified exercise, the `/setup` gate (no remote configured means `/start-sesion` and `/diagnostico` refuse), theory delivered in `leccion.md` rather than dictated in chat, the exhaustive-explanation rule, and the `/upgrade-agent` gate (written plan first, apply only on `aprobado`).

Both skills are designed for the strongest available model and instruct themselves to warn the user on a light model before proceeding. Skill instructions assume a POSIX `sh` (no brace expansion) and reference `/mnt/user-data/outputs/` for deliverables, which is the claude.ai sandbox path.
