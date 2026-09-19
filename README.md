# AI Learning Marketplace

Marketplace de plugins de [Claude Code](https://code.claude.com/docs) enfocado en **aprender cualquier cosa con un tutor de IA**.

La idea: en vez de buscar un curso, te "jalas" estas skills desde Claude Code y el agente te construye la ruta y el tutor. Dos pasos:

1. **Investiga y diseña el currículo** → un roadmap de estudio en `.md`, con fases, criterios de dominio verificables y capstone.
2. **Convierte ese roadmap en un repo-tutor** → un proyecto donde Claude Code hace de tutor personal: sesiones de ~30 min, ejercicios con tests, progreso versionado en git y notas en Obsidian.

## Instalación

Desde cualquier sesión de Claude Code:

```
/plugin marketplace add pliperkiller/ai-learning-marketplace
/plugin install learning-path@pliperkiller-learning
```

Si el resumen de instalación dice `Run /reload-plugins to activate`, córrelo.

Para verificar:

```
/plugin
```

## Uso

### Paso 1 — Generar el roadmap

Abre Claude Code en una carpeta vacía (la que será tu espacio de estudio) y usa el **modelo más potente disponible**: ambas skills hacen investigación y diseño curricular, y con un modelo ligero la calidad cae.

```
/learning-path:generate-study-roadmap quiero aprender Rust para sistemas embebidos, ~10 h/semana
```

O simplemente: *"quiero aprender X"* — la skill se dispara sola.

Sale un `roadmap-<tema>.md`. **Refínalo en la conversación** antes de seguir: quitar fases, cambiar herramientas, ajustar el alcance. Es más barato corregir aquí que después.

### Paso 2 — Generar el repo-tutor

Con el roadmap ya en la sesión:

```
/learning-path:create-learning-agent
```

Produce `tutor-<tema>.zip`. Descomprímelo, entra con Claude Code y:

```
/setup         # se autoconfigura
/diagnostico   # ubica tu nivel real con preguntas puntuales
/start-sesion  # arranca la primera sesión
```

De ahí en adelante el repo se maneja solo con sus propios commands: `/start-sesion`, `/end-sesion`, `/repaso`, `/estado`, `/fase`, `/config`, `/upgrade-agent`.

### Actualizar un tutor ya generado

Los repos-tutor **no** heredan automáticamente los cambios de la skill. Cuando actualices el plugin (`/plugin update learning-path@pliperkiller-learning`), entra al repo del tutor y corre `/upgrade-agent`: migra el motor conservando roadmap, progreso, notas y ejercicios.

## Qué hay adentro

```
.claude-plugin/marketplace.json     # catálogo
plugins/
└── learning-path/
    ├── .claude-plugin/plugin.json
    ├── README.md
    └── skills/
        ├── generate-study-roadmap/  # paso 1
        └── create-learning-agent/   # paso 2
```

| Skill | Qué hace |
|---|---|
| `generate-study-roadmap` | Investiga el tema en la web (consenso de skills, demanda del perfil, certificaciones, tendencias) y produce un roadmap por fases con criterios de dominio demostrables. |
| `create-learning-agent` | Deriva `roadmap.yaml`, genera el repo-tutor completo (CLAUDE.md pedagógico, 9 slash commands, ejercicios con tests, vault de Obsidian, estado en git), lo valida y lo entrega en `.zip`. |

## Desarrollo local

Antes de hacer push, valida y prueba desde la carpeta del repo:

```bash
claude plugin validate .
```

```
/plugin marketplace add ./ai-learning-marketplace
/plugin install learning-path@pliperkiller-learning
```

Añadido desde un directorio local, el plugin se carga en sitio: los cambios que hagas a los `SKILL.md` se ven sin reinstalar (puede hacer falta `/reload-plugins`).

Para publicar una versión nueva: sube `version` en `plugins/learning-path/.claude-plugin/plugin.json` **y** en la entrada del `marketplace.json`, o los usuarios se quedan con la copia cacheada. Si tocas el motor del repo-tutor (`assets/repo/`), sube también `metadata.version` en el `SKILL.md` de `create-learning-agent` y agrega la entrada en su `references/changelog.md` — ese changelog es lo que hace posible el `/upgrade-agent` de los repos existentes.

## Agregar más skills

Para una skill nueva del mismo flujo de aprendizaje: carpeta bajo `plugins/learning-path/skills/<nombre>/SKILL.md`. Se auto-descubre, no hay que declararla en ningún lado.

Para algo de otro dominio: un plugin nuevo bajo `plugins/` con su `.claude-plugin/plugin.json`, más una entrada en el array `plugins` del `marketplace.json`.

> Las skills de un plugin no pueden referenciar archivos fuera de su directorio (`../`): al instalar, Claude Code copia solo el directorio del plugin. Si dos plugins necesitan compartir assets, duplícalos o usa symlinks.

## Licencia

MIT
