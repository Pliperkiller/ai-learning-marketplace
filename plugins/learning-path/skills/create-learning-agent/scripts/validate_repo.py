#!/usr/bin/env python3
"""Validate a tutor repo generated (or upgraded) by create-learning-agent.

Usage:
    python3 validate_repo.py <repo-dir> [--fresh] [--diff-base <git-ref>] [--version X.Y]

Options:
    --fresh            The repo was just generated: setup and diagnostico must be
                       "pendiente", topicos empty, pendiente null, no session notes.
    --diff-base REF    Post-upgrade check: compare the working tree against REF
                       (normally HEAD) and fail if any student-zone file changed,
                       except additive changes to progress.json and to the
                       frontmatter of topic notes.
    --version X.Y      Expected state/agente.json version. Defaults to
                       metadata.version of the SKILL.md next to this script.

Exit code 0 = OK (warnings allowed), 1 = errors.
"""

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: pyyaml is required: pip install pyyaml (add --break-system-packages if pip demands it)")
    sys.exit(1)

COMMANDS = ["setup", "start-sesion", "end-sesion", "diagnostico", "repaso",
            "estado", "fase", "config", "upgrade-agent"]
TIPOS = {"codigo", "mixto", "conceptual"}
GATE_ESTADOS = {"en_curso", "completado"}
RUTAS = {"saltar", "expres", "completo"}
PLACEHOLDER_KEYS = ["TEMA", "SLUG", "HERRAMIENTAS_EVAL", "EJEMPLO_TEST",
                    "LABS_EJEMPLOS", "REQUISITOS_EXTRA", "STACK_GITIGNORE"]
REQUIRED_FILES = [
    "CLAUDE.md", "README.md", ".gitignore",
    "roadmap/roadmap.yaml", "docs/roadmap.md", "docs/upgrades/_plantilla.md",
    "state/progress.json", "state/agente.json",
    "material/README.md", "material/.obsidian/app.json", "material/.obsidian/graph.json",
    "material/sesiones/_plantilla.md",
    "ejercicios/README.md", "ejercicios/_plantilla/leccion.md",
    "ejercicios/_plantilla/enunciado.md", "labs/README.md",
]
# Student zone: any change against --diff-base is an error, except the two
# hybrid patterns checked semantically below.
STUDENT_ZONE = ["roadmap/roadmap.yaml", "docs/roadmap.md", "material/fase-*/*.md",
                "material/sesiones/????-??-??.md", "ejercicios/fase-*/**",
                "ejercicios/diagnostico/**", "labs/*/**"]
HYBRID = ["state/progress.json", "material/fase-*/*.md"]
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z_]+\}\}")
SANITIZE_RE = re.compile(r'[/\\:*?"<>|#^\[\]]')

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def split_frontmatter(text):
    """Return (frontmatter_dict_or_None, body). Body is the text after the closing ---."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        return None, text
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None, text
    return (fm if isinstance(fm, dict) else None), m.group(2)


def matches_zone(rel, patterns):
    return any(fnmatch.fnmatch(rel, p) for p in patterns)


def expected_version(explicit):
    if explicit:
        return explicit
    skill_md = Path(__file__).resolve().parent.parent / "SKILL.md"
    if not skill_md.exists():
        return None
    fm, _ = split_frontmatter(skill_md.read_text(encoding="utf-8"))
    return str((fm or {}).get("metadata", {}).get("version", "")) or None


# --------------------------------------------------------------------------- checks

def check_files(repo):
    for rel in REQUIRED_FILES:
        if not (repo / rel).exists():
            err(f"falta {rel}")
    for c in COMMANDS:
        if not (repo / ".claude/commands" / f"{c}.md").exists():
            err(f"falta .claude/commands/{c}.md")
    for stale in ["break", "sesion"]:
        if (repo / ".claude/commands" / f"{stale}.md").exists():
            err(f".claude/commands/{stale}.md no existe desde 2.2: debe eliminarse")


def check_gates(data):
    """gates_fase: one entry per phase that already went through its entry gate."""
    gates = data.get("gates_fase")
    if gates is None:
        return
    if not isinstance(gates, dict):
        err("progress.json: gates_fase debe ser un objeto {fase_id: {...}}")
        return
    for fase_id, gate in gates.items():
        if not isinstance(gate, dict):
            err(f"progress.json: gates_fase.{fase_id} debe ser un objeto")
            continue
        estado = gate.get("estado")
        if estado not in GATE_ESTADOS:
            err(f"progress.json: gates_fase.{fase_id}.estado inválido {estado!r} "
                f"(esperado: {' | '.join(sorted(GATE_ESTADOS))})")
        rutas = gate.get("rutas")
        if rutas is None:
            continue
        if not isinstance(rutas, dict):
            err(f"progress.json: gates_fase.{fase_id}.rutas debe ser un objeto {{topic_id: ruta}}")
            continue
        for tid, ruta in rutas.items():
            if ruta not in RUTAS:
                err(f"progress.json: gates_fase.{fase_id}.rutas.{tid} inválida {ruta!r} "
                    f"(esperado: {' | '.join(sorted(RUTAS))})")


def check_progress(repo, fresh):
    p = repo / "state/progress.json"
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"state/progress.json no parsea: {e}")
        return None
    for key in ["setup", "diagnostico", "gates_fase", "topicos", "posicion_actual", "pendiente",
                "fortalezas", "debilidades", "sesiones_completadas", "ultima_sesion", "_reglas"]:
        if key not in data:
            err(f"progress.json: falta la clave '{key}'")
    setup = data.get("setup") or {}
    if "estado" not in setup:
        err("progress.json: setup.estado ausente")
    diag = data.get("diagnostico") or {}
    for key in ["estado", "nivel_global", "niveles_por_fase"]:
        if key not in diag:
            err(f"progress.json: diagnostico.{key} ausente")
    check_gates(data)
    if fresh:
        if setup.get("estado") != "pendiente":
            err("--fresh: setup.estado debe ser 'pendiente'")
        if diag.get("estado") != "pendiente":
            err("--fresh: diagnostico.estado debe ser 'pendiente'")
        if data.get("topicos"):
            err("--fresh: topicos debe estar vacío")
        if data.get("gates_fase"):
            err("--fresh: gates_fase debe estar vacío")
        if data.get("pendiente") is not None:
            err("--fresh: pendiente debe ser null")
    return data


def check_roadmap(repo):
    p = repo / "roadmap/roadmap.yaml"
    if not p.exists():
        return []
    try:
        rm = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        err(f"roadmap.yaml no parsea: {e}")
        return []
    topics, ids, total = [], set(), 0
    meta = rm.get("meta") or {}
    for fase in rm.get("fases") or []:
        for key in ["id", "nombre", "horas", "criterio_dominio_fase", "capstone", "topicos"]:
            if key not in fase:
                err(f"roadmap.yaml: fase {fase.get('id', '?')} sin '{key}'")
        total += fase.get("horas") or 0
        for t in fase.get("topicos") or []:
            tid = t.get("id")
            if not tid:
                err(f"roadmap.yaml: tópico sin id en {fase.get('id')}")
                continue
            if tid in ids:
                err(f"roadmap.yaml: id duplicado {tid}")
            ids.add(tid)
            if not t.get("nombre"):
                err(f"roadmap.yaml: {tid} sin nombre")
            if t.get("tipo") not in TIPOS:
                err(f"roadmap.yaml: {tid} tipo inválido {t.get('tipo')!r}")
            if not t.get("criterio_dominio"):
                err(f"roadmap.yaml: {tid} sin criterio_dominio")
            topics.append((fase.get("id"), t))
    if meta.get("horas_totales_estimadas") != total:
        err(f"roadmap.yaml: meta.horas_totales_estimadas={meta.get('horas_totales_estimadas')} "
            f"pero la suma de fases es {total}")
    return topics


def check_manifest(repo, version):
    p = repo / "state/agente.json"
    if not p.exists():
        return
    try:
        m = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"state/agente.json no parsea: {e}")
        return
    if m.get("skill") != "create-learning-agent":
        err("agente.json: skill debe ser 'create-learning-agent'")
    if version and str(m.get("version")) != str(version):
        err(f"agente.json: version={m.get('version')!r}, esperada {version!r}")
    ph = m.get("placeholders") or {}
    for key in PLACEHOLDER_KEYS:
        val = ph.get(key)
        if not isinstance(val, str) or not val.strip():
            err(f"agente.json: placeholders.{key} vacío o ausente")
        elif PLACEHOLDER_RE.search(val):
            err(f"agente.json: placeholders.{key} sigue sin sustituir")
    for key in ["personalizaciones", "upgrades"]:
        if not isinstance(m.get(key), list):
            err(f"agente.json: '{key}' debe ser una lista")


def check_seed_notes(repo, topics, progress):
    """One note per topic, frontmatter topic_id matches, prerequisite wikilinks resolve."""
    notes = {}  # topic_id -> path
    names = set()  # note file stems (wikilink targets)
    for path in repo.glob("material/fase-*/*.md"):
        names.add(path.stem)
        fm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
        if fm is None:
            err(f"{path.relative_to(repo)}: frontmatter ausente o inválido")
            continue
        tid = fm.get("topic_id")
        if tid:
            notes[tid] = path
        for key in ["fase", "tipo", "estado", "nivel", "tags"]:
            if key not in fm:
                err(f"{path.relative_to(repo)}: frontmatter sin '{key}'")
        if progress and tid:
            status = (progress.get("topicos") or {}).get(tid, {}).get("status", "no_visto")
            if fm.get("estado") != status:
                warn(f"{path.relative_to(repo)}: estado={fm.get('estado')} pero progress.json dice {status} "
                     "(progress.json manda; se corrige en el próximo /end-sesion)")
    for fase_id, t in topics:
        tid = t["id"]
        if tid not in notes:
            err(f"tópico {tid} sin nota semilla en material/fase-*/")
            continue
        expected_name = SANITIZE_RE.sub("", t["nombre"]).strip()
        if notes[tid].stem != expected_name:
            warn(f"{notes[tid].relative_to(repo)}: el nombre de archivo no coincide con el nombre del tópico "
                 f"({expected_name!r}); el grafo mostrará el nombre del archivo")
    for path in repo.glob("material/fase-*/*.md"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("**Prerequisitos:**"):
                for link in re.findall(r"\[\[([^\]|#]+)", line):
                    if link.strip() not in names:
                        err(f"{path.relative_to(repo)}: prerequisito [[{link}]] no apunta a una nota existente")
                break


def check_placeholders(repo):
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo).as_posix()
        if rel.startswith(".git/") or "/.obsidian/" in f"/{rel}" or rel.startswith("material/.obsidian/"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        hits = sorted(set(PLACEHOLDER_RE.findall(text)))
        if not hits:
            continue
        if matches_zone(rel, STUDENT_ZONE):
            warn(f"{rel}: contiene {', '.join(hits)} (zona del estudiante: se ignora)")
        else:
            err(f"{rel}: placeholders sin sustituir {', '.join(hits)}")


def check_fresh_sessions(repo):
    extra = [p.name for p in repo.glob("material/sesiones/*.md") if p.name != "_plantilla.md"]
    if extra:
        err(f"--fresh: material/sesiones/ no debe tener notas de sesión: {extra}")


# --------------------------------------------------------------------------- diff-base

def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def subset_equal(old, new, path="", ignore_top=("_reglas", "version")):
    """Every key in old must exist in new with an equal value (recursively). Extra keys in new are fine."""
    problems = []
    if isinstance(old, dict) and isinstance(new, dict):
        for k, v in old.items():
            if not path and k in ignore_top:
                continue
            here = f"{path}.{k}" if path else k
            if k not in new:
                problems.append(f"clave eliminada: {here}")
            else:
                problems += subset_equal(v, new[k], here, ignore_top)
    elif old != new:
        problems.append(f"valor cambiado: {path or '<raíz>'}")
    return problems


def check_diff_base(repo, base):
    r = git(repo, "diff", "--name-status", base, "--")
    if r.returncode != 0:
        err(f"git diff contra {base} falló: {r.stderr.strip()}")
        return
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        status, rel = parts[0], parts[-1]
        if not matches_zone(rel, STUDENT_ZONE) and not matches_zone(rel, HYBRID):
            continue
        if status.startswith(("D", "R")):
            err(f"zona del estudiante: {rel} fue {'borrado' if status[0] == 'D' else 'renombrado'}")
            continue
        if status.startswith("A"):  # staged addition: allowed for topic notes, otherwise must be in the plan
            if not fnmatch.fnmatch(rel, "material/fase-*/*.md"):
                warn(f"archivo nuevo en zona del estudiante: {rel} (debe estar listado en el plan)")
            continue
        old = git(repo, "show", f"{base}:{rel}").stdout
        new = (repo / rel).read_text(encoding="utf-8")
        if rel == "state/progress.json":
            try:
                for p in subset_equal(json.loads(old), json.loads(new)):
                    err(f"progress.json: {p}")
            except json.JSONDecodeError as e:
                err(f"progress.json: no parsea al comparar: {e}")
        elif fnmatch.fnmatch(rel, "material/fase-*/*.md"):
            ofm, obody = split_frontmatter(old)
            nfm, nbody = split_frontmatter(new)
            if obody.strip() != nbody.strip():
                err(f"{rel}: el cuerpo de la nota cambió")
            for p in subset_equal(ofm or {}, nfm or {}, ignore_top=()):
                err(f"{rel}: frontmatter — {p}")
        else:
            err(f"zona del estudiante: {rel} fue modificado")
    untracked = git(repo, "ls-files", "--others", "--exclude-standard").stdout.splitlines()
    for rel in untracked:
        if matches_zone(rel, STUDENT_ZONE) and not fnmatch.fnmatch(rel, "material/fase-*/*.md"):
            warn(f"archivo nuevo en zona del estudiante: {rel} (debe estar listado en el plan)")


# --------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo")
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--diff-base")
    ap.add_argument("--version")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"ERROR: {repo} no es un directorio")
        sys.exit(1)

    check_files(repo)
    progress = check_progress(repo, args.fresh)
    topics = check_roadmap(repo)
    check_manifest(repo, expected_version(args.version))
    check_seed_notes(repo, topics, progress)
    check_placeholders(repo)
    if args.fresh:
        check_fresh_sessions(repo)
    if args.diff_base:
        check_diff_base(repo, args.diff_base)

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(errors)} errores, {len(warnings)} avisos — {len(topics)} tópicos, "
          f"{len(COMMANDS)} commands esperados")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
