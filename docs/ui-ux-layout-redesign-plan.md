# Plan: rediseño UI/UX de layout (EasyTaciones)

## Principios de producto (prioridad)

El resultado debe sentirse **hermoso** (criterio visual alto, coherencia, detalle), **útil** (cada pantalla deja claro el siguiente paso y el valor), **fácil de usar** (pocas fricciones, lectura rápida, errores claros) y **no aburrido** sin caer en ruido: variedad controlada, ritmo visual, micro-momentos de “vida” (transiciones, estados, vacíos con personalidad).

| Principio | Qué significa en la práctica |
|-----------|------------------------------|
| Hermoso | Jerarquía tipográfica clara, espaciado generoso, acentos de color con intención, bordes/sombras consistentes, nada de “formulario gris genérico”. |
| Útil | CTAs obvios, filtros que explican el efecto, listados que priorizan lo urgente/relevante, feedback cuando algo tarda o falla. |
| Fácil | Navegación siempre alcanzable (móvil incluido), menos clics para lo frecuente, copy en español claro, estados vacíos que enseñan. |
| No aburrido | Motion sutil (hover, entrada de cards), ilustración o patrón de fondo ligero donde aporte, chips/badges con significado, empty states con tono humano (no mensaje seco). |

## Gestalt aplicada (percepción “mega profesional”)

La psicología de la Gestalt explica **cómo agrupamos y priorizamos** lo que vemos. Usarla de forma explícita sube la sensación de producto enterprise sin añadir ruido.

| Principio | Qué logra | Aplicación concreta en este proyecto |
|-----------|-----------|--------------------------------------|
| **Proximidad** | Lo cercano se percibe como un solo grupo | Más espacio *entre* secciones que *dentro* de una card; filtros y leyenda pegados al panel de filtros; metadatos de licitación agrupados bajo el título, no mezclados con el score. |
| **Semejanza** | Mismo estilo = misma categoría | Un solo sistema de chips (`source-chip`, `badge`, urgencia); botones primario/secundario siempre con las mismas clases; tipos de texto: una escala (eyebrow → título → cuerpo → muted). |
| **Continuidad** | El ojo sigue líneas y ejes | Alinear títulos de columnas y filas en [`tenders-table`](apps/web/components/tenders-table.tsx); ribbon y filas que compartan rejilla implícita; evitar saltos de alineación entre header de página y contenido. |
| **Cierre** | Completamos formas parciales | Cards con borde/sombra/radio coherentes para “cerrar” el grupo; listas con separadores claros para que cada oportunidad sea una unidad cerrada. |
| **Figura–fondo** | Lo importante destaca del contexto | Fondo de página vs paneles (`.panel`) con contraste suave pero claro; header sticky ya figura sobre el scroll — reforzar separación sin competir con el contenido principal. |
| **Destino común** | Lo que se mueve junto se relaciona | Animaciones cortas y **agrupadas** (abrir menú móvil: nav + auth como un bloque); evitar animar elementos aislados sin relación. |
| **Simplicidad (Prägnanz)** | Preferimos lo más claro posible | Una acción principal por vista cuando sea razonable; reducir líneas duplicadas de explicación; vacíos con un mensaje + una acción, no cinco párrafos. |
| **Región común** | Área delimitada = grupo | `PageShell` y paneles como regiones; admin en bloques delimitados; evitar “bloques flotantes” sin contenedor en formularios largos. |

**Checklist rápida de revisión (post-implementación):**

- [ ] ¿Se entiende en **5 segundos** qué es la pantalla y qué hacer después?
- [ ] ¿Los elementos relacionados están **más cerca** entre sí que con el resto?
- [ ] ¿Hay **una jerarquía** clara (un foco visual principal por viewport)?
- [ ] ¿Los patrones repetidos (badges, botones) son **reconocibles** al instante?
- [ ] ¿El fondo y los paneles mantienen **figura–fondo** sin competir?

## Contexto técnico actual

- Route groups: `(marketing)`, `(workspace)`, `(auth)`, `admin` con `route-shell`.
- [`apps/web/components/layout/page-shell.tsx`](apps/web/components/layout/page-shell.tsx): `<main>` con variantes; **uso mixto** con páginas que abren `<main>` manual.
- [`apps/web/app/layout.tsx`](apps/web/app/layout.tsx): skip link y `#main-content` ya presentes.
- **Bug móvil:** [`apps/web/app/layout-system.css`](apps/web/app/layout-system.css) define menú colapsable (`.site-nav-toggle`, `.site-nav-wrap--open`) pero [`apps/web/components/site-header.tsx`](apps/web/components/site-header.tsx) no implementa el toggle: en viewport angosto la navegación queda oculta sin forma de abrirla.

## Fase 1 — Base sólida + “belleza útil”

*(Criterio transversal Gestalt: figura–fondo en header, región común en el panel móvil, destino común en la animación del menú.)*

1. **Header móvil funcional y pulido**
   - Cliente: toggle, `aria-expanded`, foco, Escape; clase `--open` alineada al CSS existente.
   - **No aburrido / hermoso:** transición corta al abrir panel (opacity/transform ya en CSS si falta), sombra suave en overlay o borde del panel móvil para separar del fondo.

2. **Unificar `PageShell`**
   - Migrar páginas con `<main>` manual a `PageShell` para ritmo de padding/max-width uniforme (sensación de producto “diseñado”, no pegado al borde).

3. **Activo por ruta**
   - `usePathname()` para destacar ítem actual; admin company vs platform sin ambigüedad.

4. **Capa de “vida” sin recargar**
   - Revisar [`landing-ornaments.tsx`](apps/web/components/landing-ornaments.tsx) y patrones del landing: **reutilizar** motivos ligeros (gradientes, líneas, badges) en workspace en dosis pequeña (headers de sección, bandas KPI) para que el dashboard no sea plano gris.

## Fase 2 — UX de flujos (útil + fácil)

*(Criterio transversal Gestalt: proximidad entre label–control–ayuda; continuidad visual entre filtros aplicados y resultados; cierre de cada fila de oportunidad como unidad.)*

5. **Filtros**
   - `method="get"` + `action` explícitos; copy sin backticks; texto que diga qué hace “Aplicar”.
   - Opcional: loading accesible al enviar (spinner o texto “Actualizando…”).

6. **Lista de oportunidades**
   - Estado vacío con ilustración ligera o icono + 2 líneas de copy + enlace “Ver todas” / “Limpiar filtros”.
   - Móvil: ribbon menos denso o apilado; mantener jerarquía “título → meta → score”.

7. **Feedback y confianza**
   - Mensajes de éxito/error en formularios admin ya existentes: unificar tono (breve, accionable).

## Fase 3 — Sistema visual y deuda CSS

8. **Tokens**
   - Lista corta en comentario al tope de [`globals.css`](apps/web/app/globals.css): `--accent`, `--muted`, radios, sombras — objetivo: **cualquier pantalla nueva use los mismos tokens** (coherencia = se ve más “cara”).

9. **Duplicación**
   - Extraer bloques repetidos de `.site-header` / `.page-shell` a partial importado (sin cambiar paleta en el primer paso).

10. **Microcopy opcional**
    - “Ventas” → “Contacto” o similar si mejora claridad.

## Criterios de aceptación

- Móvil: menú usable y con transición agradable; foco y lectura de pantalla correctos.
- Workspace y marketing comparten **ritmo** (márgenes, tipografía) aunque distintos ornamentos.
- Vacíos y cargas no se sienten “muertos”.
- Un visitante describe la UI como **profesional y memorable**, no genérica.
- **Gestalt:** agrupación por proximidad y regiones claras; alineación y continuidad en listados/tablas; semejanza en componentes repetidos; figura–fondo legible en cada breakpoint.

## Fuera de alcance (siguiente iteración)

- Rediseño de marca completo o nueva paleta desde cero.
- Librería de componentes tipo shadcn (salvo que el equipo lo pida).
- Animaciones largas o pesadas que afecten rendimiento.

## Tareas (checklist)

- [ ] Toggle móvil + a11y + transición en `SiteHeader`
- [ ] Migrar páginas a `PageShell`
- [ ] Nav activa por pathname (`/admin/*`)
- [ ] Filtros + empty state lista + responsive lista
- [ ] Pulir tokens/comentario + extracción mínima de CSS duplicado
- [ ] Pinceladas “no aburrido”: ornamentos/bandas en workspace acordes al sistema existente
- [ ] **Paso Gestalt:** ajustar espaciados internos/externos en dashboard y detalle (proximidad + región común); alinear ribbon + cards en lista (continuidad); unificar chips/badges (semejanza); revisar contraste panel/fondo (figura–fondo)
