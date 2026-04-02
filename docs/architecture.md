# Architecture

## Bounded domains

1. `services/connectors`: extracción por fuente.
2. `services/normalization`: mapeo al modelo común.
3. `services/dedupe`: reglas híbridas de deduplicación.
4. `jobs`: ejecución explícita de ingestas.
5. `api`: endpoints de lectura y disparo manual.
6. `web`: dashboard y admin.

## Phase 1 decisions

- Persistencia directa a PostgreSQL.
- Jobs síncronos disparables por API o script.
- Un único source real inicial: COMPR.AR.
- Seed demo obligatorio para no depender del portal.

