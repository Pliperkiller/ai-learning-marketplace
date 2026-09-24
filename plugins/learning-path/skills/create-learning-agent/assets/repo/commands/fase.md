---
description: Estado detallado de una fase con estimación de fecha de cierre (solo lectura)
---
Argumentos: $ARGUMENTS
- Si viene un id de fase (`f1`, `f2`...), analiza esa fase.
- Si viene vacío, analiza la fase de `posicion_actual`.

Lee `state/progress.json`, `roadmap/roadmap.yaml` y lista `material/sesiones/` (ignora `_plantilla.md`; los nombres `YYYY-MM-DD.md` son el historial de sesiones; ábrelas solo si necesitas saber qué tópico se trabajó cada día). Luego muestra, en este orden:

1. **Tabla de tópicos de la fase** — columnas `Tópico | Estado | Ruta`. El estado va anotado, no pelado: `dominado`; `aprendido (review el <next_review>` + qué falta para dominado si aplica`)`; `visto (<motivo si está en notas>)`; `no visto`. La ruta sale de `gates_fase.<fase_id>.rutas`: `saltar`, `expres` o `completo`. Si la fase no tiene entrada en `gates_fase`, pon `—` en toda la columna y dilo en una línea: "esta fase aún no pasó por su gate de entrada; las rutas se deciden en la primera sesión de la fase". Marca `← siguiente` en el tópico de `posicion_actual`.
2. **Estimación de sesiones restantes para cerrar la fase**, como rango (p. ej. "entre 8 y 11"), con desglose por tópico pendiente:
   - Pondera por ruta cuando la fase ya pasó su gate: `saltar` = 0 sesiones (ya está en `aprendido`; solo consume reviews), `expres` = 1 sesión, `completo` = el ritmo real de abajo (o la personalización de sesiones por tópico registrada en `state/agente.json`, si existe: aplica solo a `completo`). Sin gate todavía, trata todos los tópicos pendientes como `completo` y avisa de que el gate puede bajar el número.
   - Ritmo real: sesiones por tópico = sesiones que trabajaron tópicos de esta fase ÷ tópicos que llegaron a `aprendido` o más. Si hay menos de 3 sesiones de historia, asume ~2 sesiones/tópico y dilo explícitamente.
   - Ajusta por tamaño: pondera con los `conceptos` del tópico en el yaml (un tópico gordo puede llevar 2-3, uno corto 1-2).
   - Capstone de la fase: 2-3 sesiones SIEMPRE, aunque todos los tópicos hayan quedado en `saltar` (recuérdale que el criterio de dominio de fase es el capstone, no los tópicos sueltos; el gate no lo exime).
   - Reviews pendientes: no suman sesiones extra si caben en los primeros minutos de cada sesión; menciónalo.
3. **Cadencia y fecha tentativa**: sesiones/semana a partir de las fechas de `material/sesiones/` (pesa más lo de las últimas 2-3 semanas). Traduce el rango de sesiones a una fecha aproximada: "A tu cadencia actual (<X>/semana), eso es cerrar la fase alrededor de <fecha aproximada>". Si la cadencia es irregular, da la fecha con la cadencia reciente y acláralo.
4. Cierra con 1-2 observaciones accionables: qué juega a favor, qué debilidad anotada conviene atacar.

No modifiques ningún archivo ni hagas commit.
