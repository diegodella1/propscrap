# EasyTaciones Demo Guide

Guía corta para mostrar el producto sin improvisar, dejar una cuenta usable y encaminar una prueba de 30 días.

## 1. Objetivo de la demo

La demo no tiene que mostrar “todas las features”.

Tiene que demostrar tres cosas:

- la empresa entra rápido por CUIT
- el discovery deja de ser manual y pasa a una cola priorizada
- el seguimiento y las alertas sostienen la operación diaria

## 2. Credenciales demo

### Superadmin

- URL: `/login/superadmin`
- email: `admin@propscrap.local`
- password: `Admin1234`

### Empresa demo

- URL: `/login/empresa`
- email: `manager@licitacionesia.local`
- password: `Manager1234`

## 3. Preparación antes de mostrar

Ejecutar desde la raíz del repo:

```bash
apps/api/.venv/bin/alembic -c apps/api/alembic.ini upgrade head
bash scripts/test_api.sh
bash scripts/smoke_easytaciones.sh
```

Confirmar también:

- `propscrap-web` respondiendo en `127.0.0.1:3000`
- `propscrap-api` respondiendo en `127.0.0.1:8001`
- al menos una fuente activa
- al menos una licitación visible en dashboard
- superadmin con acceso a `admin/platform`
- manager con acceso a `admin/company`

## 4. Demo de 10 minutos

### Minuto 1: Problema y promesa

Entrar a `/`.

Mensaje a transmitir:

- hoy el equipo vive entre portales, PDFs, planillas y memoria humana
- EasyTaciones unifica discovery, scoring, seguimiento y alertas
- no vende “más scraping”, vende control operativo

### Minuto 2: Alta por CUIT

Entrar a `/signup`.

Mostrar:

- ingreso de CUIT argentino
- lookup legal de empresa
- precarga de identidad
- alta orientada a entrar rápido al workspace

Mensaje:

- el producto no arranca en blanco
- la empresa entra con base legal y un perfil inicial usable

### Minuto 3 a 5: Workspace empresa

Entrar como empresa demo en `/login/empresa`.

Recorrido:

- `dashboard`
- barra de adopción del trial
- oportunidades con score, motivo y urgencia
- abrir una licitación
- mostrar dossier, IA, fechas y fuente original
- guardar o pasar a revisión desde el estado

Mensaje:

- esto ya no es “buscar”
- esto es decidir qué vale mover hoy

### Minuto 6: Pipeline

Entrar a `/saved`.

Mostrar:

- columnas de seguimiento
- licitaciones guardadas
- overrides de alertas por licitación

Mensaje:

- una oportunidad relevante pasa a cartera activa
- la empresa ya no depende de acordarse sola de todo

### Minuto 7: Mi cuenta

Entrar a `/mi-cuenta`.

Mostrar:

- canales del usuario
- WhatsApp
- Telegram
- email
- nivel de filtro personal

Mensaje:

- la empresa define la regla base
- cada usuario activa cómo quiere enterarse

### Minuto 8: Admin de empresa

Entrar a `/admin/company`.

Mostrar:

- tablero de alertas de empresa
- score mínimo default
- usuarios listos para WhatsApp, email y Telegram
- reglas default de nuevas licitaciones y fechas detectadas
- equipo de la empresa

Mensaje:

- el manager puede gobernar la operación sin pedir cambios técnicos

### Minuto 9 y 10: Superadmin

Entrar a `/login/superadmin` y luego a `/admin/platform`.

Mostrar:

- fuentes
- automatización
- credenciales operativas
- auditoría
- jobs
- outbox de alertas

Mensaje:

- la plataforma puede crecer en fuentes y conectores
- la operación global no depende de tocar código para tareas normales

## 5. Qué hacer si el cliente quiere probar 30 días

### Paso 1. Alta

- registrar la empresa por CUIT o crear el usuario inicial
- completar perfil comercial base

### Paso 2. Activación

Resolver estos tres hitos:

- canal de alertas activo
- perfil comercial razonable
- primera licitación guardada

### Paso 3. Rutina

Pedirle al equipo que haga esto durante la prueba:

- revisar `dashboard` todos los días
- guardar lo relevante
- mover estado en `saved`
- dejar nota en cada licitación activa
- validar si las alertas llegan por el canal elegido

## 6. Configuración de alertas

### Regla de empresa

Se configura en `admin/company`.

Sirve para definir:

- score mínimo para discovery
- si se avisa por nuevas licitaciones
- si se avisa por fechas detectadas
- si esas fechas aplican solo a guardadas
- con qué anticipación avisar

### Regla de usuario

Se configura en `mi-cuenta`.

Sirve para definir:

- qué canal usa cada persona
- si quiere email, WhatsApp o Telegram
- nivel de filtro personal

### Override por licitación

Se configura en `saved`.

Sirve para:

- heredar la regla de empresa o no
- activar o desactivar recordatorios para una licitación puntual
- ajustar anticipación solo para ese caso

## 7. Qué debería quedar configurado por superadmin

Antes de una prueba seria:

- fuentes activas relevantes
- `OPENAI_API_KEY` y `OPENAI_MODEL` o runtime equivalente
- `RESEND_API_KEY` y `RESEND_FROM_EMAIL` si va email
- `WHATSAPP_ENABLED` y proveedor real o mock según caso
- `TELEGRAM_ENABLED` si se usa Telegram
- canales públicos y datos de contacto

## 8. Qué debería quedar configurado por admin de empresa

- perfil comercial claro
- buyers y jurisdicciones
- exclusiones
- score mínimo
- alertas de discovery
- alertas de fechas
- usuarios internos listos para recibir avisos

## 9. Criterio para decir “la prueba va bien”

La prueba está bien encaminada si en la primera semana:

- la empresa entiende el flujo sin explicación constante
- aparecen oportunidades coherentes
- al menos una licitación entra al pipeline
- al menos un canal de alertas funciona
- el manager puede ajustar reglas desde la interfaz

## 10. Mensaje de cierre recomendado

“Lo importante no es que el producto muestre muchas pantallas. Lo importante es que en pocos días el equipo deje de depender de portales, PDFs y memoria informal para sostener oportunidades reales.”
