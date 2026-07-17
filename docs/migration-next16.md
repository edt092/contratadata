# Migración de framework — Next.js 14 → 16

Registro de la actualización de framework hecha como Fase 1 de la
transformación de marca (ver `prompt1.md`). Cubre versiones, decisiones y
bloqueos documentados, no funcionalidad de producto.

## Línea base (antes de tocar nada)

- Next 14.2.35 · React 18 · Tailwind 3.4.1 · `@clerk/nextjs` 6.9.0 ·
  TanStack Query 5.51.1 · Tremor 3.18.1 · ESLint 8 (`next lint`, sin
  `.eslintrc`/`eslint.config.*` propio) · Vitest 2.1.8.
- `tsc --noEmit`: limpio. `vitest run`: 6/6 tests verdes. `next build`:
  compilaba (el único error visible era prerender por falta de
  `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` en el entorno de auditoría, no un bug
  real — `.env.local` ya existe en el repo local del usuario con las claves).

## Versiones finales

| Paquete | Antes | Después | Nota |
|---|---|---|---|
| `next` | 14.2.35 | **16.2.10** | estable, engine `>=20.9.0` (Node local 22.14 ✓) |
| `react` / `react-dom` | ^18 | **18.3.1** | ver "React 19: por qué no" abajo |
| `@clerk/nextjs` | 6.9.0 | **7.5.20** | peer deps ahora piden `next ^16.0.10\|\|^16.1.0-0`, satisfecho |
| `@tanstack/react-query` | 5.51.1 | **5.101.2** | sin cambios de API usados por el proyecto |
| `@tremor/react` | 3.18.1 | **3.18.7** | último patch; sin versión con soporte React 19 |
| `tailwindcss` | 3.4.1 | **4.3.3** | ver sección Tailwind abajo |
| `eslint` | 8.57.1 | **9.39.5** | requerido por `eslint-config-next` 16 (`>=9.0.0`) |
| `eslint-config-next` | 14.2.0 | **16.2.10** | ahora exporta flat config nativo |
| `typescript` | ^5 | **5.9.3** | ver "TypeScript 7: por qué no" abajo |
| `vitest` / `@vitejs/plugin-react` / `@testing-library/*` | 2.1.8 / 4.3.4 / 16.0.1 | 2.1.9 / 4.7.0 / 16.3.2 | patch/minor, sin saltos de major |

## React 19: por qué no (todavía)

`prompt1.md` pedía React 19.2. Next 16 lo soporta (`react: ^18.2.0 ||
19.0.0-rc-... || ^19.0.0`), y Clerk 7 también. El bloqueo real es
**`@tremor/react`**, que declara `peerDependencies.react: "^18.0.0"` sin
excepción, y no tiene ninguna versión publicada compatible con React 19 (su
último release es de enero de 2025 — el paquete parece sin mantenimiento
activo). `BarList` de Tremor se usa activamente en `/entidad/[slug]` y
`/contratista/[slug]` (`frontend/app/entidad/[slug]/page.tsx:6`,
`frontend/app/contratista/[slug]/page.tsx`).

Decisión: **quedarse en React 18.3.1** esta iteración en vez de forzar React
19 con un peer mismatch. Next 16 permite ambas, así que no bloquea el resto
del upgrade. Plan futuro: cuando se retire `@tremor/react` (reemplazando
`BarList` por un componente propio o por las imágenes seaborn que ya
reemplazaron `AreaChart` en evolución mensual), subir a React 19 sin este
freno.

## TypeScript 7: por qué no

`typescript@latest` resuelve a **7.0.2**, el nuevo compilador nativo
(reescrito en Go, proyecto "tsgo"/TypeScript nativo). Es un cambio de
runtime del compilador, no solo de versión de lenguaje, y está fuera del
alcance de un upgrade de framework "seguro". Se fijó **5.9.3** (el último
5.x estable), que es totalmente compatible con Next 16, ESLint 9 y
`typescript-eslint` 8.

## Tailwind 3 → 4

A diferencia de lo que anticipaba el plan (que el riesgo de Tailwind 4 fuera
"romper Tremor"), el hallazgo real fue que **el proyecto casi no usa
utilidades de Tailwind directamente** — el theming es 100% variables CSS
(`--text`, `--surface`, `--primary`... en `frontend/app/globals.css`) y
clases propias (`.animate-fade`, `.row-hover`, `.btn-link`, `.nav-btn`).
Ningún componente usa el variant `dark:` de Tailwind. Confirmado por
grep: cero coincidencias de `dark:` en `app/` y `components/`.

Se migró usando el modo de compatibilidad de Tailwind v4 vía `@config`, que
reutiliza `tailwind.config.ts` (content globs, `darkMode: 'class'`,
`fontFamily`) sin reescribirlo:

- `frontend/postcss.config.js`: `tailwindcss` → `@tailwindcss/postcss`
  (Tailwind v4 ya no necesita `autoprefixer` por separado — se eliminó del
  `package.json`).
- `frontend/app/globals.css`: `@tailwind base/components/utilities` →
  `@import "tailwindcss"; @config "../tailwind.config.ts";`
- `frontend/tailwind.config.ts`: sin cambios.

Verificación: `next build` compila limpio; se inspeccionó el CSS generado
(`.next/static/chunks/*.css`) y se confirmó que utilidades reales usadas en
componentes propios (`mt-2` en `TopEntidadesChart.tsx`, `h-56 mt-2` en
`CalidadChart.tsx`) se generan correctamente con la nueva sintaxis de escala
de espaciado de v4 (`calc(var(--spacing) * N)`), lo que confirma que el
content-scanning vía `@config` sigue funcionando sobre `app/`/`components/`.

Hallazgo aparte (no introducido por esta migración): las clases de tema
propias de Tremor (`text-tremor-content`, `dark:text-dark-tremor-content`,
etc., usadas dentro de `BarList`) nunca se generaron ni en Tailwind 3, porque
`tailwind.config.ts` nunca registró el preset de color de Tremor
(`theme.extend.colors` con la paleta `tremor-*`). Es una brecha
preexistente, no una regresión — queda documentada para quien retome el
reemplazo de Tremor.

## `middleware.ts` → `proxy.ts`

Next 16 deprecó el nombre `middleware.ts` en favor de `proxy.ts` (el runtime
pasa a ser exclusivamente `nodejs`, ya no soporta `edge` —
[nextjs.org/docs/messages/middleware-to-proxy](https://nextjs.org/docs/messages/middleware-to-proxy)).
Se renombró el archivo preservando el comportamiento exacto: sigue siendo
solo `clerkMiddleware()` sin gating de rutas (la autorización real vive en
`useMe()`/`PremiumGate` del lado del cliente y en
`src/api/deps.py::require_pro` del backend — ver comentario en
`frontend/proxy.ts`). El build confirma el reconocimiento correcto:
`ƒ Proxy (Middleware)` en la salida de `next build`.

## ESLint: `next lint` → CLI + flat config

`eslint-config-next` 16 ya exporta un flat config nativo (`Linter.Config[]`)
en su entrada principal — no hace falta el puente `FlatCompat`/`.eslintrc`
(se probó primero con `FlatCompat` y falló con
`TypeError: Converting circular structure to JSON`, un problema conocido al
envolver un preset ya-flat con el compatibilizador legacy). Config final en
`frontend/eslint.config.mjs`:

```js
import nextConfig from 'eslint-config-next'
export default [...nextConfig, { ignores: ['node_modules/**'] }]
```

`package.json`: `"lint": "next lint"` → `"lint": "eslint ."`.

### Errores nuevos que ESLint 9 / `eslint-plugin-react-hooks` 7 detectaron

El upgrade de `eslint-config-next` trajo `eslint-plugin-react-hooks@^7`, que
añade reglas nuevas orientadas a compatibilidad con el compilador de React
(`react-hooks/immutability`, `react-hooks/set-state-in-effect`). Se
corrigieron los 13 errores reales encontrados (no se desactivó ninguna
regla):

- `react/no-unescaped-entities` (6 ocurrencias en `alertas/page.tsx`,
  `competidores/page.tsx`, `SaveAlertButton.tsx`): comillas rectas literales
  en JSX → comillas tipográficas `“ ”`.
- `react-hooks/immutability` en
  `frontend/app/contratista/[slug]/page.tsx`: un `let acc = 0` mutado dentro
  de un `.map()` para calcular offsets acumulados de un donut chart se
  reescribió como `.reduce()` puro (acumulador threaded por el propio
  reduce, sin variable externa mutable).
- `react-hooks/set-state-in-effect` en `frontend/components/FeedbackModal.tsx`
  (reset de `status` al abrir el modal): se reemplazó el `useEffect` por el
  patrón de React "ajustar estado durante el render"
  (`if (open !== prevOpen) { setPrevOpen(open); ...}`), documentado en
  [react.dev](https://react.dev/learn/you-might-not-need-an-effect#adjusting-some-state-when-a-prop-changes).
- `react-hooks/set-state-in-effect` en
  `frontend/components/WompiCheckoutButton.tsx`: se quitaron las llamadas
  `setCheckout(null)`/`setError(false)` síncronas al inicio del efecto
  (redundantes — ya son los valores iniciales de `useState`) y se movió el
  reset de error/checkout a los propios manejadores `.then()`/`.catch()`.

Quedan 4 warnings (no errores, no bloquean `lint`) de
`@next/next/no-img-element` en `Navbar.tsx`, `cuenta/page.tsx` y
`ChartImage.tsx` — conversión a `next/image` pendiente para la Fase 7
(requiere configurar `images.remotePatterns` para el avatar de Clerk y las
imágenes de gráficas servidas por la API), no se tocó aquí para no mezclar
riesgo de layout con el upgrade de framework.

## `next.config.mjs` y `tsconfig.json`

- `next.config.mjs` no necesitó cambios (estaba vacío).
- `next build` en Next 16 ajustó automáticamente `tsconfig.json`:
  `target: "ES2017"`, `jsx: "react-jsx"` (antes `"preserve"`), y agregó
  `.next/dev/types/**/*.ts` a `include` (soporte de tipos de Turbopack dev).
  Cambios generados por Next mismo, no manuales.

## Verificación final de la Fase 1

- `pnpm install`: limpio.
- `tsc --noEmit`: limpio.
- `eslint .`: 0 errores, 4 warnings (`no-img-element`, documentado arriba).
- `vitest run`: 6/6 tests verdes.
- `next build` (Turbopack): compila limpio, genera las 12 rutas existentes
  sin cambios de comportamiento, `ƒ Proxy (Middleware)` reconocido.

## Deuda técnica declarada

- React 19 bloqueado por `@tremor/react` (sin fecha de resolución — depende
  de si Tremor retoma mantenimiento o de si se reemplaza `BarList`).
- TypeScript 7 (compilador nativo) no evaluado — candidato para una
  iteración dedicada, no mezclado con este upgrade.
- 4 warnings `no-img-element` pendientes para la Fase 7 de rendimiento.
