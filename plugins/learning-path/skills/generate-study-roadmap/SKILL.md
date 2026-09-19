---
name: generate-study-roadmap
description: 'Genera un roadmap de estudio estándar en .md para cualquier tema que el usuario quiera aprender, investigando en la web (demanda del perfil, consenso de skills, certificaciones, tendencias) y estructurándolo en fases con criterios de dominio verificables y capstone evolutivo. Úsala SIEMPRE que el usuario invoque /learning-path:generate-study-roadmap (o /generate-study-roadmap), pida "un roadmap para aprender X", "plan/ruta de estudio de X", "learning path", o diga "quiero aprender X" con intención de estructurar el aprendizaje completo de un tema — aunque no use la palabra roadmap. Es el paso 1 de un flujo de dos partes cuyo paso 2 es la skill create-learning-agent, que convierte el roadmap en un repo-tutor. Diseñada para ejecutarse con el modelo más potente disponible.'
---

# Generate Study Roadmap

Produce un roadmap de estudio en `.md`, listo para refinarse en conversación y para alimentar la skill `create-learning-agent` (que lo convierte en un repo-tutor para Claude Code). El estándar de calidad: un documento investigado, secuencial, con criterios de dominio que se puedan demostrar — no un inventario de herramientas.

## Requisito de modelo

Esta skill está diseñada para el modelo más potente disponible (investigación + diseño curricular exigen profundidad). Si estás corriendo en un modelo ligero (familia Haiku o equivalente), advierte al usuario ANTES de empezar que la calidad será menor y recomiéndale repetir la invocación con el modelo más capaz; continúa solo si lo confirma.

## Paso 0 — Entender el encargo

- Extrae de `$ARGUMENTS` / el mensaje y de la conversación: **tema**, **enfoque** (p. ej. "Rust *para IA*") y **restricciones** (nivel objetivo, horas disponibles, sin certificaciones, stack preferido...).
- El roadmap es **estándar y desde cero** salvo que el usuario pida lo contrario. No lo personalices al historial o perfil del usuario: la ubicación personal la hará después el agente tutor con su diagnóstico.
- Haz máximo 1 pregunta aclaratoria, y solo si el tema es genuinamente ambiguo. Si no, procede y declara los supuestos en una línea.

## Paso 1 — Investigar (web_search, 3-6 búsquedas)

1. Consenso de roadmap y skills del tema en el año actual: `"<tema> roadmap <año>"`, `"<tema> skills"`.
2. Si el tema es profesional: demanda y proyección del perfil: `"<perfil> job outlook demand <año>"`. Reporta el panorama honesto (incluye señales negativas si existen) y el horizonte temporal de las proyecciones.
3. Si existen: certificaciones vigentes: `"<tema> certifications <año>"`.
4. Tendencias / hacia dónde va el campo: `"<tema> trends <año>"`.

Reglas: queries de 1-6 palabras; prioriza fuentes originales y recientes; parafrasea siempre (nunca cites más de 15 palabras de una fuente, máximo 1 cita por fuente). Si el tema no es profesional (un hobby, un arte, un idioma), omite demanda y certificaciones y busca en su lugar progresión de habilidad y métodos de práctica reconocidos.

## Paso 2 — Diseñar con estos principios

1. **Profundidad sobre amplitud**: una herramienta representativa por categoría, no el zoológico completo.
2. **Primero lo que no caduca**: fundamentos transferibles antes que herramientas de moda.
3. **Sesgo hacia donde va el campo**: lo que la investigación del Paso 1 indique, no lo que era estándar hace 3 años.
4. **La IA como copiloto**: asume que lo repetitivo se automatiza; el roadmap entrena el criterio que no.
5. **Certificaciones como señal, no como fin** (solo si aplican al tema).

Estructura: **6-9 fases secuenciales**. Cada fase con: objetivo (1 línea), conceptos, tecnologías/herramientas, **criterio de dominio VERIFICABLE**, certificación ancla (si aplica) y horas estimadas. Las fases nacen del tema investigado — no calques la estructura de otro dominio.

El criterio de dominio es la pieza más importante: debe poder demostrarse con código o un entregable concreto ("implementa X y explica Y", nunca "entiende X"), porque el agente tutor lo usará para diagnosticar y evaluar.

## Paso 3 — Escribir el archivo

- Sigue exactamente la estructura de `assets/plantilla-roadmap.md` (léela antes de escribir).
- Nombre del archivo: `<slug>-roadmap.md`, con un slug corto que combine enfoque y tema (ejemplo: "Rust para mis proyectos de IA" → `ai-rust-roadmap.md`). Guárdalo en `/mnt/user-data/outputs/` y preséntalo con `present_files`.
- Incluye siempre: mapa general (tabla fases/horas/certificación), criterios de dominio por fase, tabla de certificaciones priorizadas (si aplican), **proyecto transversal** (capstone evolutivo: un solo proyecto que crece fase a fase), estimación de tiempo según ritmo semanal (incluye la fila de "solo sesiones de 30 min/día"), y fuentes con URLs.

## Paso 4 — Cerrar en el chat

Resumen breve (2-4 frases) de la lógica del roadmap; si investigaste demanda, el hallazgo clave con sus citas; e invita a refinar fases, alcance o herramientas en la conversación antes de generar el agente con `/learning-path:create-learning-agent`.

## Errores a evitar

- Roadmaps-inventario: 40 herramientas sin secuencia ni prioridad.
- Criterios de dominio no verificables.
- Calcar fases de otro dominio que el tema no comparte.
- Responder solo en el chat sin crear y presentar el archivo `.md`.
- Ocultar señales negativas del mercado cuando la investigación las muestra.
