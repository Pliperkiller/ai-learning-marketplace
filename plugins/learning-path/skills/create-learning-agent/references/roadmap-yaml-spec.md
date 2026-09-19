# Schema de roadmap/roadmap.yaml

El YAML es la versión del roadmap que el tutor consume para hacer tracking tópico a tópico. Se deriva del `.md` fuente: cada fase del documento se convierte en una entrada de `fases`, y sus conceptos se agrupan en tópicos del tamaño de 2-6 sesiones de 30 minutos.

## Reglas de derivación

1. **IDs**: `f<n>.<slug-corto>` (`f1.sql-avanzado`, `f3.ownership-borrowing`). Únicos en todo el archivo, estables (el progreso del estudiante los referencia).
2. **Granularidad**: un tópico ≈ 2-6 sesiones. Una fase de un `.md` bien hecho produce 4-8 tópicos. Si el `.md` no da detalle suficiente para derivarlos, pregunta al usuario — no rellenes inventando.
3. **tipo**: `codigo` (ejercicio de producción obligatorio) | `mixto` (producción + diseño) | `conceptual` (ejercicio de diseño escrito). En dominios programables, la mayoría debe ser `codigo`.
4. **criterio_dominio**: una frase verificable por tópico — algo que el tutor pueda comprobar ejecutando o revisando un entregable. Prohibido "entiende X" o "conoce Y".
5. **prerequisitos**: solo cuando cruzan fases o rompen el orden secuencial por defecto. No listes el tópico inmediatamente anterior.
6. **capstone por fase**: el incremento que esa fase aporta al proyecto transversal del roadmap.
7. **horas**: por fase, tomadas del `.md`; `meta.horas_totales_estimadas` = suma exacta.
8. **certificacion_ancla**: `null` si la fase no tiene.

## Estructura exacta

```yaml
# Roadmap de <TEMA> — versión estructurada para el tutor.
# La versión humana está en docs/roadmap.md.

meta:
  version: 1
  horas_totales_estimadas: <suma de las fases>
  reglas:
    - "Orden por defecto: secuencial (tópicos dentro de la fase, fases en orden)."
    - "prerequisitos solo se listan cuando cruzan fases o rompen el orden por defecto."
    - "tipo: codigo (ejercicio de producción obligatorio) | mixto (producción + diseño) | conceptual (ejercicio de diseño escrito)."
    - "El estado del estudiante NO vive aquí: vive en state/progress.json."

fases:
  - id: f1
    nombre: <Nombre de la fase>
    horas: <int>
    certificacion_ancla: <string o null>
    criterio_dominio_fase: >
      <El criterio de dominio de la fase tal como está en el .md — el
      diagnóstico lo usa para calibrar el ejercicio de verificación de la fase.>
    capstone: "<Incremento del proyecto transversal en esta fase.>"
    topicos:
      - id: f1.<slug>
        nombre: <Nombre del tópico>
        tipo: codigo
        conceptos: [<concepto 1>, <concepto 2>, <concepto 3>]   # de aquí salen las preguntas de sondeo del diagnóstico: sé concreto
        tecnologias: [<herramienta 1>, <herramienta 2>]         # idem: comandos/APIs nombrables, no categorías vagas
        criterio_dominio: "<Frase verificable con un entregable concreto.>"
      - id: f1.<otro-slug>
        nombre: <...>
        tipo: conceptual
        conceptos: [<...>]
        tecnologias: []
        criterio_dominio: "<...>"
  - id: f2
    nombre: <...>
    horas: <int>
    certificacion_ancla: null
    criterio_dominio_fase: >
      <...>
    capstone: "<...>"
    topicos:
      - id: f2.<slug>
        nombre: <...>
        tipo: mixto
        prerequisitos: [f1.<slug>]   # solo si rompe el orden por defecto
        conceptos: [<...>]
        tecnologias: [<...>]
        criterio_dominio: "<...>"
```

## Validación mínima (Paso 3 de la skill)

- `yaml.safe_load` sin errores.
- IDs únicos; todo tópico con `id`, `nombre`, `tipo` ∈ {codigo, mixto, conceptual} y `criterio_dominio` no vacío.
- Toda fase con `criterio_dominio_fase`, `capstone` y `horas`.
- `sum(fase.horas) == meta.horas_totales_estimadas`.
