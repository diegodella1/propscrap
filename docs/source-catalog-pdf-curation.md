# Curacion del catalogo desde el PDF

Fecha de trabajo: 2026-04-12
PDF base: `/home/diego/Documents/prop/fuentes/Licitaciones IA Listado Fuentes para Dev.pdf`

## Criterio usado

No meti todo el PDF como si cada item valiera lo mismo. Lo separé en cuatro grupos:

- `worth_pursuing=true`: fuente publica, con pagina oficial identificable y volumen potencial razonable.
- `worth_pursuing=false`: existe, pero hoy no justifica el costo de integracion o duplica demasiado a `COMPR.AR` / `CONTRAT.AR`.
- `access=login_required`: fuente costosa para automatizar en esta etapa.
- `access=referencia_oficial`: el PDF la nombra y hay referencia oficial, pero no detecte un endpoint publico suficientemente claro para scrapearla sin trabajo previo de discovery.

## Fuentes que quedaron mejoradas o priorizadas

- `licitaciones-caba`: URL oficial de consulta de compras y contrataciones de GCBA.
- `licitaciones-santa-fe`: portal oficial publico con endpoint Ajax activo y automatizado.
- `licitaciones-mendoza`: portal `comprar.mendoza.gov.ar`.
- `licitaciones-tucuman`: portal oficial de compras provincial.
- `licitaciones-salta`: portal oficial con buscador publico.
- `licitaciones-chaco`: portal oficial con resultados publicos.
- `arsat`: pagina especifica de compras y contrataciones.
- `pami`: pagina especifica de compras y contrataciones.
- `inta`: portal de compras propio.

## Fuentes agregadas desde el PDF que faltaban

- `licitaciones-santiago-del-estero`
- `licitaciones-jujuy`
- `licitaciones-formosa`
- `licitaciones-catamarca`
- `licitaciones-la-rioja`

Las agregue al catalogo para no perderlas, pero no todas quedaron priorizadas. Catamarca y La Rioja quedaron mejor perfiladas. Santiago del Estero, Jujuy y Formosa quedaron como referencias oficiales hasta validar un endpoint de compras mas estable.

## Fuentes deliberadamente no priorizadas

- Universidades nacionales: muchisimo volumen agregado, pero nula homogeneidad como fuente unica.
- Empresas privadas grandes: casi todas requieren login o portal de proveedores.
- Vialidad Nacional, ANSES, AFIP/ARCA, CONICET: probables duplicados parciales de `COMPR.AR` o `CONTRAT.AR`; conviene integrarlas solo si aparecen gaps concretos.
- YPF: relevante, pero hoy es mas caro por acceso y operacion que por cobertura incremental.

## Siguiente corte razonable

1. Implementar primero `PAMI`, `INTA`, `Córdoba`, `Catamarca` o `San Luis`.
2. Medir volumen nuevo real contra `COMPR.AR` / `CONTRAT.AR`.
3. Recién despues decidir si vale la pena abrir el frente de empresas estatales con login o universidades.

## Gobierno posterior a la curación

Una vez incorporada una fuente al catálogo:

- se registra en el inventario maestro
- el super admin decide si la activa globalmente
- el admin de empresa decide si la hereda o la habilita para su cuenta

Detalle operativo completo en [docs/source-governance.md](source-governance.md).
