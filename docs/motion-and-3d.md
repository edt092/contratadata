# Motion y 3D — arquitectura objetivo (no implementada aún)

Esta iteración implementó la landing (`docs/brand-homepage.md`) con un
`HeroVisual` en HTML/SVG puro (`frontend/components/marketing/HeroVisual.tsx`)
en vez de la escena 3D en tiempo real que pide `prompt1.md`. Este documento
es la especificación de esa escena y de la integración de GSAP para cuando
se retome — no se instalaron `three`, `@react-three/fiber`,
`@react-three/drei` ni `gsap`/`@gsap/react` todavía.

## Por qué se difirió

Construir una escena R3F de calidad (instancing, límites de DPR, boundaries,
fallback, presupuesto de bundle medido) es un trabajo sustancial por sí
solo. Meterlo en la misma iteración que el upgrade de framework y la
reestructuración de rutas habría diluido la calidad de ambos. `HeroVisual`
ya es HTML/SVG real (no un placeholder gris) y ocupa exactamente el lugar
donde la escena 3D se insertará después, así que el reemplazo es aislado.

## Concepto: "Contract Intelligence Graph"

- Nodos pequeños = procesos. Nodos medianos = contratistas. Nodos
  principales = entidades.
- Las conexiones aparecen gradualmente (no todas a la vez).
- Un pulso identifica una nueva oportunidad — ya prototipado en 2D en
  `HeroVisual` (el nodo central con `<animate>` de radio/opacidad).
- Cámara con movimiento sutil, nunca "videojuego".
- El cursor puede generar una reacción limitada (parallax leve, no arrastre
  libre).
- Al hacer scroll, el grafo se transforma en la interfaz de búsqueda (la
  sección `ProductDemoSection` actual sería el destino de esa transición).
- Nada de globo 3D genérico ni mapa de Colombia literal.

## Arquitectura de componentes

```
components/marketing/
  HeroVisual.tsx          — hoy: SVG/CSS. Mañana: swap por HeroScene3D.
  three/
    HeroScene3D.tsx        — 'use client', carga dinámica (next/dynamic, ssr:false)
    ContractGraph.tsx       — la escena R3F en sí (nodos, líneas, pulso)
    WebGLBoundary.tsx       — detecta soporte WebGL, si no hay, renderiza HeroVisual (fallback HTML actual)
    Scene3DErrorBoundary.tsx — error boundary de React alrededor de HeroScene3D
    useVisibility.ts        — IntersectionObserver: pausa el render loop fuera de viewport
```

Reglas no negociables (ya aplicadas en el `HeroVisual` actual y que deben
mantenerse al hacer el swap):

- El contenido esencial del hero (titular, subtítulo, CTAs) es HTML normal
  fuera del canvas — nunca depende de que WebGL cargue.
- `WebGLBoundary` prueba soporte de WebGL2 (`canvas.getContext('webgl2')`)
  antes de montar R3F; si falla, renderiza `HeroVisual` (SVG) tal cual está
  hoy — ya sirve como fallback real, no solo como placeholder de desarrollo.
- Carga dinámica: `next/dynamic(() => import('./HeroScene3D'), { ssr: false })`
  — nunca importar `three`/`@react-three/fiber` en `app/layout.tsx` ni en
  ningún Server Component.
- DPR limitado (`gl={{ dpr: [1, 1.5] }}` en el `<Canvas>` de R3F).
- Instancing (`InstancedMesh`) para los nodos — no una `<mesh>` por nodo.
- `useVisibility` + `frameloop="demand"` o pausa manual cuando el hero sale
  del viewport (scroll profundo en la landing).
- Ningún texto SEO dentro del canvas — todo el copy vive en el DOM.
- `useReducedMotion()` (`frontend/lib/useReducedMotion.ts`, ya existe) debe
  detener animaciones continuas de cámara/pulso — igual que hoy detiene los
  `<animate>` SMIL del SVG.
- Cleanup explícito de geometrías/materiales/listeners en el `useEffect` de
  desmontaje — medir con Chrome DevTools memory profiler que no haya fugas
  al navegar entre `/` y otras rutas repetidamente.
- Medir el peso agregado al bundle (`next build` reporta el tamaño de la
  page `/`) antes/después de añadir Three.js — el objetivo es que
  `/explorar` (dashboard, sin 3D) no cargue nada de este código en absoluto,
  gracias a que vive solo dentro del route group `(marketing)`.

## GSAP

Tampoco instalado todavía. Cuando se añada:

- `gsap` + `@gsap/react` (hook `useGSAP` para lifecycle/cleanup automático).
- Registro centralizado de plugins (`ScrollTrigger`) en un único punto,
  p.ej. `frontend/lib/gsap.ts`, importado solo donde se usa.
- Tokens de motion ya definidos en `frontend/app/globals.css`
  (`--motion-fast: 150ms`, `--motion-standard: 300ms`,
  `--motion-editorial: 600ms`, `--motion-cinematic: 1200ms`,
  `--ease-standard`, `--ease-editorial`) — GSAP debe leer estos valores
  (vía `getComputedStyle` o duplicados como constantes JS) en vez de
  inventar duraciones nuevas, para que CSS y GSAP compartan la misma
  sensación de marca.

Usos previstos (de `prompt1.md`):
- Entrada editorial del hero (`HeroSection`).
- Transformación del grafo 3D → interfaz de búsqueda al hacer scroll.
- Revelado de métricas de confianza (`TrustMetricsSection`).
- Secuencia de aparición de `ProductsSection`.
- Scroll storytelling puntual — no scroll-hijacking agresivo.

Explícitamente prohibido (ya evitado en la Fase 4 actual, que usa CSS puro
para `animate-fade`/hover states):
- Animar cada botón permanentemente.
- Reemplazar transiciones CSS simples que ya funcionan.
- Ocultar contenido esencial antes de hidratar.
- Ejecutar animaciones para usuarios con `prefers-reduced-motion`.

## Presupuesto de rendimiento

Antes de instalar Three.js/GSAP, capturar el `next build` actual de `/`
como línea base (tamaño de "First Load JS") y comparar después de cada
adición. Si el bundle de `/` crece por encima de lo razonable para un LCP
< 2.5s en móvil, mover la escena a un `next/dynamic` con `loading:` más
agresivo o reconsiderar el instancing antes de aceptar la regresión.
