# Landing de marca — decisiones de contenido y diseño

La nueva landing vive en `app/(marketing)/page.tsx`, compuesta de 12
secciones (`frontend/components/marketing/sections/`). Este documento
explica las decisiones de contenido que no son obvias leyendo el código.

## Dirección creativa aplicada

- **Paleta**: fondo casi negro cálido (`--brand-bg: #0A0F0D`) con verde
  esmeralda/eléctrico (`--brand-primary: #16E8A0`) como señal principal,
  azul y ámbar como acentos secundarios (`--brand-accent-blue`,
  `--brand-accent-amber`) — nunca morado genérico de SaaS.
- **Tipografía**: Inter (sans, ya existente) para todo el cuerpo, Instrument
  Serif (nuevo, un solo peso) solo en titulares de marca (`H1`, `H2` de
  cada `SectionHeading`, CTA final), JetBrains Mono (ya existente) para
  microetiquetas, badges de fuente y cifras.
- **Motion**: CSS puro esta iteración (transiciones de hover, `<animate>`
  SMIL en `HeroVisual`, `prefers-reduced-motion` respetado en ambos casos
  — ver `frontend/lib/useReducedMotion.ts`). GSAP/Three.js quedan
  documentados para la siguiente iteración (`docs/motion-and-3d.md`).
- **Sin folclore colombiano obvio**: no hay bandera, mapa ni tricolor —
  "Colombia" aparece solo en el copy, no como decoración visual.

## Por sección — qué es real y qué es demo

| Sección | Contenido |
|---|---|
| Hero | Copy real. `HeroVisual` es una representación abstracta (SVG), no datos reales — es decorativo (`aria-hidden`). |
| Demostración de producto | **Datos de ejemplo**, etiquetados explícitamente "Vista de producto — datos de ejemplo" en la propia UI, porque la API no expone "procesos abiertos" filtrables hoy. |
| Métricas de confianza | **Datos reales** — `GET /pipeline/stats` (`api.globalStats()`, ya existía). Skeleton mientras carga, nunca un número inventado si falla. |
| Productos (Explore/Signal/Ask) | Explore y Signal marcados "Disponible" porque son funcionalidad real (dashboard, alertas, competidores). Ask marcado "Próximamente" — no existe implementación. |
| Fuentes primarias | SECOP II marcado "conectado" (es la fuente real del pipeline, vía Socrata). El resto (SECOP I, TVEC, PAA, Datos Abiertos, CCE) marcado "próximamente" — ninguna se consume hoy. |
| Cómo funciona / Casos de uso | Copy editorial, sin datos que verificar. |
| Experiencia Signal | Mockup estático de un flujo de alerta ya real (`/alertas` existe), con "Webhook/WhatsApp" explícitamente etiquetado "Futuro". |
| Experiencia Ask | Preview conceptual con badge "Vista previa — no funcional todavía" — nunca se presenta como un chat funcional. La cita de ejemplo usa una URL real de SECOP II (no inventada), pero el texto de respuesta es ilustrativo. |
| Planes | Gratis y Profesional con los datos reales de `/premium` (mismo precio, `$149.000/mes`). Equipo/API/Enterprise como "Contáctanos"/no ofertados — el backend no puede cobrarlos todavía. |
| FAQ | Respuestas reales sobre el estado actual del producto, con datos estructurados `FAQPage` (JSON-LD) para SEO/AI Overviews. |
| CTA final / Footer | Copy de marca + aclaración de independencia respecto al Estado colombiano (footer, y repetida en `/sobre`). |

No se inventaron testimonios, clientes, certificaciones ni logos
institucionales, tal como pide `prompt1.md`.

## SEO

- `app/(marketing)/page.tsx` exporta su propio `metadata` (title/description/
  canonical) — ya no depende del título genérico del root layout.
- Schema.org `Organization` y `WebApplication` (JSON-LD) en la landing;
  `FAQPage` en `FAQSection`.
- `/premium`, `/explorar` y `/sobre` ganaron `layout.tsx`/metadata propios
  (antes no tenían metadata específica) con canonical.
- `public/sitemap.xml` ahora incluye `/explorar` y `/premium` además de
  `/` y `/sobre`.
- No se encontró mojibake (`Ã`, `Â`...) en el código existente al auditar
  — el copy nuevo se escribió directamente en UTF-8 correcto.

## Deuda pendiente para la siguiente iteración

- `HeroVisual` (SVG) → escena R3F real (`docs/motion-and-3d.md`).
- GSAP para scroll storytelling (mismo documento).
- Assets de Hyperframes para fallback de video/OG (`docs/hyperframes-pipeline.md`).
- Avatares de Clerk y las imágenes de gráficas de `ChartImage.tsx` siguen
  usando `<img>` en vez de `next/image` — requiere configurar
  `images.remotePatterns` en `next.config.mjs` para el dominio de Clerk y
  el de la API, y no se hizo en esta iteración para no arriesgar romper
  imágenes en producción sin poder verificarlas visualmente contra datos
  reales. Las 4 instancias del logo estático (`/favicon.svg`) sí se
  migraron a `next/image`.
- `/sobre` sigue usando los tokens del dashboard (`--text`/`--muted`) en
  vez de `--brand-*` — es legible sobre el fondo de marca pero no está
  completamente re-diseñada; no era parte del alcance pedido para esta
  iteración.
