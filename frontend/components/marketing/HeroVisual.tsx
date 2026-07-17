'use client'

import { useReducedMotion } from '@/lib/useReducedMotion'

const NODES = [
  { x: 60, y: 80, r: 3, delay: 0 },
  { x: 160, y: 40, r: 5, delay: 0.4 },
  { x: 260, y: 110, r: 2.5, delay: 0.8 },
  { x: 340, y: 60, r: 4, delay: 1.2 },
  { x: 420, y: 140, r: 3, delay: 0.2 },
  { x: 120, y: 200, r: 4, delay: 0.6 },
  { x: 230, y: 220, r: 7, delay: 1 },
  { x: 330, y: 210, r: 3, delay: 1.4 },
  { x: 420, y: 250, r: 2.5, delay: 0.3 },
  { x: 70, y: 280, r: 3, delay: 1.6 },
]

const EDGES: [number, number][] = [
  [0, 1], [1, 2], [2, 3], [3, 4], [1, 6], [5, 6], [6, 7], [7, 8], [5, 9], [6, 9], [0, 5],
]

/** Representación abstracta de "Contract Intelligence Graph" — nodos (procesos,
 * contratistas, entidades) conectándose. HTML/SVG puro, sin WebGL: es el
 * punto de reemplazo futuro por la escena real de React Three Fiber (ver
 * docs/motion-and-3d.md). Puramente decorativo (`aria-hidden`) — el
 * contenido del hero es texto normal, nunca depende de este visual. */
export default function HeroVisual() {
  const reducedMotion = useReducedMotion()

  return (
    <svg
      aria-hidden
      viewBox="0 0 480 320"
      className="h-full w-full"
      style={{ opacity: 0.9 }}
    >
      <defs>
        <radialGradient id="hv-glow" cx="50%" cy="45%" r="65%">
          <stop offset="0%" stopColor="var(--brand-primary)" stopOpacity="0.16" />
          <stop offset="100%" stopColor="var(--brand-primary)" stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect x="0" y="0" width="480" height="320" fill="url(#hv-glow)" />

      {EDGES.map(([a, b], i) => (
        <line
          key={i}
          x1={NODES[a].x}
          y1={NODES[a].y}
          x2={NODES[b].x}
          y2={NODES[b].y}
          stroke="var(--brand-border)"
          strokeWidth="1"
        />
      ))}

      {NODES.map((n, i) => (
        <circle
          key={i}
          cx={n.x}
          cy={n.y}
          r={n.r}
          fill={i === 6 ? 'var(--brand-primary)' : 'var(--brand-accent-blue)'}
          opacity={0.85}
        >
          {!reducedMotion && (
            <animate
              attributeName="opacity"
              values="0.35;0.95;0.35"
              dur="3.6s"
              begin={`${n.delay}s`}
              repeatCount="indefinite"
            />
          )}
        </circle>
      ))}

      {/* Pulso sobre el nodo principal — "una oportunidad emergiendo del sistema" */}
      <circle cx={NODES[6].x} cy={NODES[6].y} r={NODES[6].r} fill="none" stroke="var(--brand-primary)" strokeWidth="1.5">
        {!reducedMotion && (
          <>
            <animate attributeName="r" values="7;28;7" dur="3.6s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.6;0;0.6" dur="3.6s" repeatCount="indefinite" />
          </>
        )}
      </circle>
    </svg>
  )
}
