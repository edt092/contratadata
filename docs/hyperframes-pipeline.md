# Hyperframes — evaluación y pipeline propuesto (no instalado)

`prompt1.md` pide usar [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)
como herramienta de referencia para producir renders de video/loops
cinematográficos a partir de HTML. Este documento registra la verificación
que pide el prompt (README, licencia, arquitectura) antes de decidir cómo
se integraría, y dónde queda ese trabajo — no se instaló como dependencia
en esta iteración.

## Verificación hecha

- **README leído** (vía `gh repo view heygen-com/hyperframes`): "HyperFrames
  is an open-source framework for turning HTML, CSS, media, and seekable
  animations into deterministic MP4 videos." Se usa vía CLI local
  (`npx hyperframes init/preview/render`) o vía "skills" que enseñan a un
  agente de código (Claude Code, Cursor, etc.) a escribir composiciones.
- **Licencia**: Apache 2.0 — permisiva, compatible con uso comercial, sin
  restricción de copyleft. Verificado en el badge del README
  (`license-Apache%202.0`).
- **Requisitos**: Node.js ≥ 22 (el entorno local ya tiene 22.14 — cumple) y
  **FFmpeg** instalado aparte (no verificado en este entorno; se necesita
  antes de renderizar).
- **Arquitectura**: no es una librería que se `import` en tiempo de
  ejecución de una app Next.js. Es un **proyecto/CLI independiente**: cada
  composición vive en su propio directorio (`npx hyperframes init
  my-video`), con su propio `preview`/`render`. Internamente compone
  animaciones vía runtimes existentes (GSAP, Three.js, Lottie, CSS/WAAPI,
  Anime.js) sobre HTML con atributos `data-*` de timing.

## Decisión de integración

**Hyperframes se usa como herramienta externa de generación de assets, no
como dependencia de producción del frontend.** Razones:

1. El prompt lo pide explícitamente: "No lo conviertas automáticamente en
   dependencia de producción."
2. Arquitectónicamente no está pensado para eso — es un renderer offline
   que produce archivos MP4/WebM, no un componente React en runtime.
3. Mantiene `frontend/package.json` limpio de una dependencia pesada
   (FFmpeg, Node 22 mínimo) que no todo el equipo necesita para desarrollar
   la web en sí.

## Pipeline propuesto

```
media/hyperframes/                    ← nuevo directorio, fuera de frontend/
  hero-loop/                          ← una composición por asset
    composition.html                  ← escena HTML/CSS reutilizable
    frame.md                          ← parámetros de marca (tokens de globals.css traducidos a "frame.md")
  README.md                           ← cómo regenerar los assets
```

1. **Escena HTML/React reutilizable** — idealmente la misma marcación
   conceptual que `HeroVisual.tsx` (mismos tokens de color
   `--brand-primary`, `--brand-bg`, etc.), adaptada al formato de
   composición de Hyperframes (`data-*` de timing en vez de SMIL/CSS vars
   de React).
2. **Parámetros de marca** vía `frame.md` — Hyperframes tiene un flujo
   dedicado (`frame.md`) para traducir un design system web a tokens de
   video; se alimentaría con los mismos valores de
   `frontend/app/globals.css` (paleta `.marketing`, radii, motion tokens).
3. **Render** con `npx hyperframes render` → MP4 determinista.
4. **Export WebM** adicional para navegadores que lo prefieran (mejor
   compresión que MP4 en muchos casos).
5. **Poster AVIF/WebP** — primer frame exportado como imagen estática, para
   `<video poster="...">` y como fallback si el video no carga.
6. **Optimización** — comprimir el MP4/WebM final (por ejemplo con
   `ffmpeg -crf`) antes de subirlo a `frontend/public/`.
7. **Uso con `<video>` responsive**:
   ```html
   <video
     poster="/media/hero-loop-poster.avif"
     autoplay muted loop playsinline
     preload="none"
   >
     <source src="/media/hero-loop.webm" type="video/webm" />
     <source src="/media/hero-loop.mp4" type="video/mp4" />
   </video>
   ```
8. **Fallback estático** — si `prefers-reduced-motion` o `navigator.connection.saveData`
   están activos, renderizar solo el poster (o el `HeroVisual` SVG actual)
   en vez de montar el `<video>`.
9. **Lazy loading** — `preload="none"` + montar el `<video>` vía
   `IntersectionObserver` solo cuando el hero entra en viewport (mismo
   patrón que `useVisibility` propuesto en `docs/motion-and-3d.md`).
10. **Respeto por reduced motion y Save-Data** — chequeo explícito antes de
    autoplay, igual que ya hace `useReducedMotion()` para el SVG actual.

## Usos previstos

- Fondo o loop cinematográfico alternativo al `HeroVisual` en vivo (para
  navegadores sin WebGL, como complemento al fallback SVG).
- Assets de Open Graph / redes sociales (clip corto del concepto de marca).
- Material para presentaciones o pitch decks del equipo.
- Assets reproducibles por agentes: como Hyperframes está diseñado para
  integrarse con agentes de código, permitiría regenerar variantes de
  marca (por ejemplo un loop distinto por temporada de licitaciones) sin
  intervención manual de diseño.

## Qué falta antes de adoptarlo

- Instalar FFmpeg en el entorno donde se vaya a renderizar (no es
  necesario en el entorno de desarrollo/build normal del frontend).
- Decidir si `media/hyperframes/` vive en este mismo repositorio o en uno
  separado de assets de marca — no se decidió en esta iteración porque
  todavía no hay una escena 3D/HTML final que renderizar (depende de que
  se construya primero `HeroScene3D` según `docs/motion-and-3d.md`).
- Ninguna dependencia de npm (`hyperframes`) se agregó a
  `frontend/package.json` — se invocaría vía `npx` solo en el flujo de
  generación de assets, nunca en `next build`/`next dev`.
