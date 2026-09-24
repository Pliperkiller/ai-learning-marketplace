---
description: Cerrar la sesión en curso ahora mismo — ceremonia de cierre completa (estado, notas, commit, push)
---
El estudiante indica que la sesión termina en este momento. Ejecuta el protocolo /end-sesion definido en CLAUDE.md, completo y en orden, sin importar en qué punto quedó la sesión (ejercicio terminado, a medias o sin empezar):

1. Evalúa lo hecho (ejercicio, repasos, preguntas de la lección).
2. Actualiza `state/progress.json`: status y `next_review` de los tópicos tocados, `debilidades`, `posicion_actual`, `sesiones_completadas`, `ultima_sesion`, y `pendiente` (objeto con `topic_id`, `ejercicio`, `paso`, `siguiente` si quedó trabajo a medias; `null` si no). Si la sesión fue el gate de una fase, escribe además `gates_fase.<fase_id>` = `{estado: "completado" o "en_curso" si quedaron tópicos sin retar, fecha, rutas: {topic_id: saltar|expres|completo}, evidencia: {topic_id: "<una línea con el porqué>"}}`, y aplica el efecto de las rutas `saltar` (`status: aprendido`, `nivel: alto`, `next_review` = hoy + 2).
3. Sincroniza las notas de tópico en `material/fase-N/` (apuntes, errores, frontmatter, links según la regla).
4. Escribe la nota de sesión `material/sesiones/YYYY-MM-DD.md`.
5. `git add -A && git commit -m "sesion <N>: <topic_id> — <resultado>" && git push`. Si el push falla, dilo y no des la sesión por cerrada.
6. Confirma en ≤4 líneas qué cambió y qué quedó pendiente, y cierra con "Retoma con `/start-sesion`". Si fue un gate de fase, cierra en cambio con la tabla `Tópico | Ruta | Por qué` y la estimación recalculada de la fase.

Reglas: `aprendido` solo con ejercicio verificado; nunca `dominado` en la sesión en que se enseñó el tópico. Si no hay sesión abierta ni cambios por guardar, dilo y no toques archivos.
