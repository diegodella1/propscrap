# Gobierno de fuentes y habilitación comercial

Fecha: 2026-04-13

## Objetivo

Dejar explícito cómo entra una fuente nueva al producto y quién puede habilitarla en cada capa.

## Flujo operativo

1. La fuente se registra en el catálogo maestro.
2. Se implementa y registra su conector en backend.
3. El super admin decide si queda `is_active=true` a nivel plataforma.
4. Si está activa globalmente, pasa a estar disponible en el inventario principal o "top de licitaciones".
5. Cada admin de empresa decide si su cuenta:
   - hereda todas las fuentes activas
   - o usa un subconjunto custom
6. Los usuarios finales de esa empresa sólo ven licitaciones provenientes de las fuentes efectivamente habilitadas para su empresa.

## Capas de decisión

### 1. Catálogo maestro

Archivos principales:

- `apps/api/app/services/source_catalog.py`
- `apps/api/app/services/source_registry.py`

Acá se define:

- slug
- nombre
- `base_url`
- `connector_slug`
- `scraping_mode`
- `config_json`
- si la fuente está activa globalmente

Esta capa define qué existe en el producto.

### 2. Super admin

Pantalla:

- `/admin/platform`

El super admin:

- da de alta o ajusta una fuente del inventario
- decide si queda activa globalmente
- revisa salud de corridas, errores y métricas

Si una fuente está inactiva globalmente, no debe ser visible para empresas ni usuarios finales.

### 3. Admin de empresa

Pantalla:

- `/admin/company`

El admin de empresa no crea fuentes nuevas.

Solo puede decidir el alcance de su empresa dentro del universo ya habilitado por superadmin:

- `all_active`: hereda todo lo globalmente activo
- `custom`: elige un subset puntual

## Regla efectiva de visibilidad

La visibilidad final de una licitación depende de dos filtros:

1. La fuente debe estar activa globalmente.
2. La fuente debe estar incluida en el alcance de la empresa.

Si falla cualquiera de los dos, la licitación no debe entrar al discovery de esa empresa.

## Estado actual de fuentes nuevas

Fuentes ya activadas y con conector operativo:

- `pami`
- `inta`
- `licitaciones-cordoba`
- `licitaciones-catamarca`
- `licitaciones-san-luis`
- `licitaciones-rio-negro`
- `licitaciones-tucuman`
- `licitaciones-corrientes`

## Caso especial: GCBA

GCBA ya no está bloqueada a nivel de modelo de datos ni de ingestión. El bloqueo real es sólo la captura del listado público desde este host.

Estado actual:

- la tabla pública de aperturas próximas fue validada con HTML/HAR real
- el detalle ciudadano `/PLIEGO/VistaPreviaPliegoCiudadano.aspx?qs=...` es público
- el backend ya puede consumir `data/staging/gcba.json`
- ese JSON entra por el mismo pipeline que cualquier otra fuente

Flujo operativo:

1. Un operador o job externo captura `ListarAperturaProxima.aspx` desde un navegador/host que vea la grilla real.
2. Se guarda `HAR` o `HTML`.
3. Se ejecuta:
   - `apps/api/.venv/bin/python scripts/export_gcba_json.py --har ...`
   - o `apps/api/.venv/bin/python scripts/sync_gcba_staging.py --har ...`
4. El super admin decide cuándo pasar `licitaciones-caba` a activa globalmente.
5. Recién ahí los admins de empresa pueden heredarla o incluirla en modo custom.

Regla comercial:

- `implemented=true` no implica `is_active=true`
- GCBA hoy está implementada en modo `staged_json`
- queda inactiva globalmente hasta que la captura quede automatizada de forma confiable

## Nota específica sobre Corrientes

Corrientes expone un backend público en:

- `https://nportal.cgpc.gob.ar/documentos/apiweb/generic?novedad=true`

Ese feed mezcla licitaciones vigentes con archivo histórico.

Para que la fuente sea usable en discovery, el conector actual aplica estos recortes:

- sólo entradas de `seleccion = Licitaciones`
- exclusión de pliegos para evitar duplicados
- ventana de recencia por `fecha_publicacion` de 120 días

Eso deja la fuente operativa para el top de licitaciones sin inundar la base con histórico viejo.
