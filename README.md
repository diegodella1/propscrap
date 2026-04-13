# EasyTaciones

Producto operativo para empresas argentinas que venden al Estado. El foco es consolidar fuentes reales, registrar la empresa por CUIT, priorizar oportunidades y sostener el seguimiento con alertas y administración usable.

- setup local de backend y frontend
- esquema inicial de base de datos
- tracking de `sources` y `source_runs`
- persistencia de `tenders`
- primer conector real para COMPR.AR
- dashboard inicial con listado y filtros básicos
- seed demo para no depender del portal en vivo

## Estado actual

Phase 1:

- setup local de backend y frontend
- esquema inicial
- conector real COMPR.AR
- dashboard de listado

Phase 2:

- 3 fuentes activas: `COMPR.AR`, `Boletín Oficial`, `PBAC`
- detalle real de licitación
- descarga de documentos para Boletín Oficial
- extracción nativa de texto PDF con `PyMuPDF`
- Next.js actualizado a `15.5.14`

Phase 3:

- OCR fallback con `tesseract` cuando el PDF nativo es pobre
- enriquecimiento LLM estructurado con OpenAI Responses API
- resumen IA visible en la página de detalle

Phase 4:

- perfil demo de empresa
- matching explicable con score y razones
- filtro de relevancia en dashboard

Phase 5:

- workflow states básicos
- alerts persistidos por relevancia y vencimientos
- admin/debug funcional

Phase 6+:

- landing comercial separada del dashboard operativo
- dashboard, detalle y admin con sistema visual unificado
- frontend preparado para proxy local `/api` hacia FastAPI
- script simple de arranque para demo local
- split de login entre empresa y superadmin
- alta de empresa por CUIT con perfil comercial inicial
- superadmin con fuentes, automatización, auditoría y ABM global
- release checklist y smoke listos para salida a campo

## Stack

- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Frontend: Next.js App Router
- Base de datos: PostgreSQL local
- Infra local: `docker-compose` o cualquier Postgres compatible, incluyendo Supabase local

## Estructura

```text
apps/
  api/   FastAPI, modelos, jobs, conectores
  web/   Next.js dashboard
data/
  seeds/ datos demo y snapshots
  documents/ almacenamiento local de archivos
docs/
scripts/
```

## Requisitos

- Python 3.11+
- Node 22+
- npm 10+
- Docker

## Arranque local

1. Levantar Postgres:

```bash
docker compose up -d postgres
```

2. Configurar entorno:

```bash
cp .env.example .env
```

3. Backend:

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
alembic upgrade head
python ../../scripts/seed_demo.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Frontend:

```bash
cd apps/web
npm install
npm run dev
```

5. Demo stack listo para mostrar:

```bash
bash scripts/start_demo_stack.sh
```

Esto deja:

- frontend en `http://127.0.0.1:3000`
- backend en `http://127.0.0.1:8001`
- el frontend proxyeando `/api` y `/health` al backend local

## Endpoints útiles

- `GET /health`
- `GET /api/v1/tenders`
- `GET /api/v1/tenders/{id}`
- `GET /api/v1/sources`
- `GET /api/v1/source-runs`
- `POST /api/v1/jobs/ingest/comprar`
- `POST /api/v1/jobs/ingest/boletin-oficial`
- `POST /api/v1/jobs/ingest/pbac`
- `POST /api/v1/jobs/process/{tender_id}`
- `POST /api/v1/jobs/enrich/{tender_id}`
- `POST /api/v1/jobs/match/{tender_id}`
- `POST /api/v1/jobs/match-all`
- `POST /api/v1/jobs/alerts/generate`
- `POST /api/v1/jobs/alerts/dispatch`
- `POST /api/v1/tenders/{tender_id}/state`

## Jobs útiles

```bash
cd apps/api
.venv/bin/python ../../scripts/run_ingestion.py comprar
.venv/bin/python ../../scripts/run_ingestion.py boletin-oficial
.venv/bin/python ../../scripts/run_ingestion.py pbac
.venv/bin/python ../../scripts/process_tender.py 27
.venv/bin/python ../../scripts/enrich_tender.py 27
.venv/bin/python ../../scripts/match_tenders.py
curl -X POST http://127.0.0.1:8000/api/v1/jobs/alerts/generate
curl -X POST http://127.0.0.1:8000/api/v1/jobs/alerts/dispatch
```

## Variables LLM

```bash
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
LLM_ENABLED=true
```

Si `OPENAI_API_KEY` no está definido, el job de enriquecimiento falla explícitamente.

## WhatsApp alerts

- cada usuario puede definir `whatsapp_number`, opt-in, verificación y preferencias de alertas
- la generación crea alerts por usuario y por canal
- el dispatch de WhatsApp se ejecuta con `POST /api/v1/jobs/alerts/dispatch` o `python scripts/dispatch_alerts.py`
- con `WHATSAPP_PROVIDER=mock` y `WHATSAPP_ENABLED=true`, los mensajes quedan persistidos en `data/outbox/whatsapp_messages.jsonl`
- con `WHATSAPP_PROVIDER=meta`, configurar `WHATSAPP_META_TOKEN` y `WHATSAPP_META_PHONE_NUMBER_ID`

## Telegram alerts

- cada usuario puede definir `telegram_chat_id`, opt-in y preferencias de canal
- el dispatch de Telegram usa bot API
- configurar `TELEGRAM_ENABLED=true` y `TELEGRAM_BOT_TOKEN`
- desde superadmin también se puede sobrescribir la configuración sin tocar `.env`

## Auth y perfil propio

- `POST /api/v1/auth/signup` crea usuario y abre sesión
- `POST /api/v1/auth/login` inicia sesión
- `POST /api/v1/auth/logout` cierra sesión
- `GET /api/v1/me` devuelve el usuario autenticado
- `PATCH /api/v1/me` deja editar nombre, empresa, WhatsApp y preferencias simples
- el flujo público vive en `/signup`, `/login`, `/login/empresa`, `/login/superadmin` y `/mi-cuenta`

## Nota sobre Supabase local

La app usa PostgreSQL estándar. Si preferís apuntar al Postgres de Supabase local, cambiá `DATABASE_URL` y listo. En esta fase no dependemos de Auth, Storage ni Realtime.

## Release readiness

- checklist operativa: [docs/launch-readiness.md](docs/launch-readiness.md)
- guía de demo y prueba de 30 días: [docs/demo-guide.md](docs/demo-guide.md)
- gobierno de fuentes y habilitación comercial: [docs/source-governance.md](docs/source-governance.md)
- validación reproducible: `bash scripts/release_readiness_check.sh`
- smoke funcional: `bash scripts/smoke_easytaciones.sh`
- arranque demo local: `bash scripts/start_demo_stack.sh`

## Rutas principales

- `/` landing comercial
- `/about` cómo funciona
- `/signup` alta por CUIT
- `/login/empresa` acceso cliente
- `/login/superadmin` acceso plataforma
- `/dashboard` discovery operativo
- `/saved` pipeline de seguimiento
- `/company-profile` perfil comercial
- `/admin/company` administración de empresa
- `/admin/platform` consola superadmin

## Servicios persistentes

- `deploy/propscrap-api.service` publica la API en `127.0.0.1:8001`
- `deploy/propscrap-web.service` publica el frontend en `127.0.0.1:3000`
- `deploy/propscrap-scheduler.service` publica el worker de automatización
- `deploy/propscrap-pilot-check.timer` corre un chequeo cada 15 minutos sobre base, ciclo y fuentes activas
- ambos usan `Restart=always` para reiniciar automáticamente después de un reboot o corte de luz
- después de cambios en frontend, reconstruí `apps/web` con `npm run build` antes de reiniciar `propscrap-web`
- `docker-compose.yml` deja Postgres en `127.0.0.1:55432` con `restart: unless-stopped` para no chocar con Supabase local

## Pendiente para siguientes fases

- robustecer OCR sobre PDFs escaneados más complejos
- ejecutar enriquecimiento LLM real con `OPENAI_API_KEY`
- sumar mejores controles operativos y retries sobre jobs
