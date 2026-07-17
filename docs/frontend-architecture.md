# Arquitectura frontend

Resumen de la fundación construida en la Iteración 1 de la transformación de
marca (ver `prompt1.md`). Para el detalle del upgrade de framework ver
`docs/migration-next16.md`; para la landing en sí, `docs/brand-homepage.md`;
para 3D/motion/video, `docs/motion-and-3d.md` y `docs/hyperframes-pipeline.md`.

## Route groups

```
frontend/app/
  layout.tsx          # RootLayout: ClerkProvider, QueryProvider, ThemeProvider,
                       # FeedbackProvider, fuentes (next/font), metadata base.
                       # Ya NO renderiza un header — cada grupo pone el suyo.
  globals.css          # tokens compartidos + paleta .marketing (ver abajo)

  (marketing)/          # público, layout = MarketingHeader + Footer
    layout.tsx
    page.tsx             # landing → "/"
    premium/
      layout.tsx           # metadata (la page es 'use client', no puede exportarla)
      page.tsx              # → "/premium"
    sobre/page.tsx          # → "/sobre"

  (product)/             # dashboard/cuenta, layout = Navbar (el de siempre)
    layout.tsx
    explorar/
      layout.tsx            # metadata
      page.tsx               # dashboard (antes vivía en app/page.tsx) → "/explorar"
    entidad/[slug]/page.tsx  # → "/entidad/[slug]" (URL sin cambios)
    contratista/[slug]/page.tsx
    alertas/page.tsx
    competidores/page.tsx
    cuenta/page.tsx
    pipeline/page.tsx

  (auth)/                # Clerk, layout = wordmark + link a "/"
    layout.tsx
    sign-in/[[...sign-in]]/page.tsx
    sign-up/[[...sign-up]]/page.tsx
```

Los route groups (`(marketing)`, `(product)`, `(auth)`) no aparecen en la
URL — solo agrupan layouts. Ninguna URL existente se rompió: la única que
cambia de *contenido* es `/`, que pasó de ser el dashboard a ser la landing
(el dashboard sigue vivo, completo, en `/explorar`). Ver `docs/migration-next16.md`
para la lista exacta de archivos movidos.

## Design system

Dos capas de tokens en `frontend/app/globals.css`:

1. **Tokens del dashboard** (`--bg`, `--surface`, `--text`, `--primary`
   azul, etc.) — sin cambios, siguen gobernando `/explorar`, `/alertas`,
   `/competidores`, `/cuenta`, `/pipeline`, entidad/contratista.
2. **Tokens compartidos nuevos** (radii, sombras, blur, contenedores,
   motion durations/easings, paleta de charts) — disponibles en toda la
   app, no rompen nada porque son aditivos.
3. **Paleta de marca** (`.marketing`, verde esmeralda/eléctrico sobre fondo
   oscuro cálido) — escopeada a la clase `.marketing` que pone
   `app/(marketing)/layout.tsx` en su contenedor raíz. El dashboard nunca
   ve estos valores.

Esta separación fue deliberada: el prompt pide una identidad de marca
nueva y distinta para marketing sin heredar el azul del dashboard, pero
también pide no romper el dashboard existente. Dos paletas conviviendo por
scope CSS logra ambas cosas sin tocar `ContractsTable`, `KPICard`,
`FilterBar` ni ningún componente del dashboard.

### Componentes (`frontend/components/marketing/`)

`Container`, `Eyebrow`, `SectionHeading`, `Button` (exporta
`PrimaryButton`/`SecondaryButton` con variantes CVA), `DataMetric`,
`SourceBadge`, `VerifiedCitation`, `ProductCard`, `UseCaseCard`,
`PricingPreview`, `Footer`, `MarketingHeader`, `MobileNavigation`,
`HeroVisual` — todos nuevos, todos consumen los tokens `--brand-*`.
`Navbar.tsx` (el header del dashboard, con sus tests) **no se tocó** — se
reutiliza tal cual dentro de `(product)/layout.tsx`.

`frontend/components/marketing/sections/` tiene una sección por archivo
(`HeroSection`, `ProductDemoSection`, `TrustMetricsSection`,
`ProductsSection`, `SourcesSection`, `HowItWorksSection`,
`UseCasesSection`, `SignalExperienceSection`, `AskExperienceSection`,
`PlansPreviewSection`, `FAQSection`, `FinalCtaSection`), compuestas en
`app/(marketing)/page.tsx`.

## Trazabilidad de datos

`frontend/lib/types.ts` define `DataQuality`/`DataCitation` (el contrato de
`prompt1.md`: `updated_at`, `freshness_seconds`, `status`, `source_name`,
`source_url`, `retrieved_at`...). `VerifiedCitation` y `SourceBadge` lo
consumen. **No se migró ningún endpoint de FastAPI a esta forma todavía**
— se usa hoy solo donde ya hay evidencia real (el ejemplo de Ask usa un
`source_url` real de SECOP, no inventado). Pendiente para el backend:
exponer `quality`/`citation` en los endpoints que la landing eventualmente
consuma con datos en vivo (hoy `TrustMetricsSection` ya usa
`GET /pipeline/stats`, que es real pero no trae ese sobre de trazabilidad
explícito).

## Testing

Sin cambios de infraestructura de test (`vitest.config.ts`,
`vitest.setup.ts`, `Navbar.test.tsx`, `useFeatureGate.test.ts` intactos).
No se agregaron tests nuevos para los componentes de marketing en esta
iteración — son en su mayoría presentacionales; el punto de mayor riesgo
real (`MarketingHeader`, que replica la lógica de auth de `Navbar`) queda
como candidato más claro para un test futuro si se detecta necesidad.

## Qué se preservó intacto

Clerk, Wompi/`WompiCheckoutButton`, `useMe`/`usePremiumStatus`/`useFeatureGate`,
`PremiumGate`, alertas, competidores, reportes, tema claro/oscuro
(`ThemeProvider`), FastAPI, variables de entorno, `pnpm-lock.yaml`. Ningún
endpoint de backend se modificó.
