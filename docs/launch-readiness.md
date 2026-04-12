# EasyTaciones Launch Readiness

Checklist final para pasar de demo interna a prueba real en campo con empresas.

## 1. Release freeze

- congelar features nuevas hasta terminar el primer piloto
- trabajar solo fixes, claridad de producto y estabilidad
- definir un commit candidato de release

## 2. Infraestructura mínima

- `propscrap-web` arriba y respondiendo en `127.0.0.1:3000`
- `propscrap-api` arriba y respondiendo en `127.0.0.1:8001`
- migraciones aplicadas con `alembic upgrade head`
- backup de base previo a cualquier despliegue sensible
- `SESSION_SECRET` real en producción
- `DATABASE_URL` apuntando a la base correcta
- `CORS_ORIGINS`, `NEXT_PUBLIC_SITE_URL`, `INTERNAL_API_BASE_URL` consistentes

## 3. Variables sensibles

### Obligatorias

- `DATABASE_URL`
- `SESSION_SECRET`

### Para LLM

- `LLM_ENABLED`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`

### Para email

- `RESEND_API_KEY`
- `RESEND_FROM_EMAIL`

### Para WhatsApp

- `WHATSAPP_ENABLED`
- `WHATSAPP_PROVIDER`
- `WHATSAPP_META_TOKEN`
- `WHATSAPP_META_PHONE_NUMBER_ID`

### Para Telegram

- `TELEGRAM_ENABLED`
- `TELEGRAM_BOT_TOKEN`

### Para lookup empresa / CUIT

- `ARCA_PADRON_ARCHIVE_URL`
- `ARCA_PADRON_CACHE_HOURS`
- opcionalmente:
  - `ARCA_WS_TOKEN`
  - `ARCA_WS_SIGN`
  - `ARCA_WS_CUIT_REPRESENTADA`

## 4. Validación técnica obligatoria

Ejecutar siempre desde la raíz del repo:

```bash
bash scripts/release_readiness_check.sh
```

Esto valida:

- health de API y web
- tests unitarios actuales del backend
- build de producción del frontend
- smoke end-to-end con signup, login, dashboard, admin y fuentes

## 5. Casos de uso que deben pasar manualmente

### Deslogueado

- home
- cómo funciona
- contacto
- signup por CUIT
- login empresa
- login superadmin

### Empresa

- alta por CUIT
- precarga de perfil legal/comercial
- edición de keywords, buyers y jurisdicciones
- visualización de oportunidades
- guardar licitación
- mover licitación a seguimiento
- revisar preferencias en `mi-cuenta`

### Admin empresa

- alta de usuario
- cambio de rol interno
- desactivación
- revisión de perfil comercial

### Superadmin

- alta de fuente
- edición de fuente
- corrida manual
- revisión de runs
- revisión de outbox y alertas
- revisión de auditoría
- ABM de usuarios
- edición de automatización, LLM y canales públicos

## 6. Credenciales demo actuales

### Superadmin

- URL: `/login/superadmin`
- email: `admin@propscrap.local`
- password: `Admin1234`

### Empresa

- URL: `/login/empresa`
- email: `manager@licitacionesia.local`
- password: `Manager1234`

## 7. Go-live operativo

- desplegar build actual
- reiniciar `propscrap-web`
- verificar health
- correr `bash scripts/smoke_easytaciones.sh`
- confirmar login empresa y superadmin
- confirmar que el superadmin puede:
  - ver usuarios
  - ver fuentes
  - editar automatización

## 8. Piloto de campo recomendado

- elegir 3 a 5 empresas reales
- acompañar el onboarding inicial manualmente
- usar 2 o 3 fuentes relevantes por vertical
- medir:
  - tiempo de alta
  - tiempo hasta primera oportunidad útil
  - claridad del score/matching
  - utilidad del pipeline
  - utilidad de alertas

## 9. Señales de salida

Considerar “listo para abrir más” solo si:

- la empresa puede registrarse sola por CUIT
- entiende cómo completar el perfil comercial
- ve oportunidades coherentes con su actividad
- puede guardar y seguir licitaciones sin ayuda
- recibe alertas por al menos un canal confiable
- el superadmin puede corregir la operación sin tocar código

## 10. Rollback mínimo

- guardar commit anterior estable
- tener backup de base previo al deploy
- poder reconstruir frontend anterior
- poder reiniciar web/api con la versión anterior
