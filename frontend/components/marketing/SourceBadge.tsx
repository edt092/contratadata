import { cn } from '@/lib/utils'

interface SourceBadgeProps {
  label: string
  status?: 'connected' | 'planned'
  className?: string
}

/** Distingue fuentes de datos ya conectadas de fuentes futuras (sección
 * "Fuentes primarias" de la landing) — nunca marca una fuente como
 * conectada sin que el pipeline la consuma de verdad. */
export default function SourceBadge({ label, status = 'connected', className }: SourceBadgeProps) {
  const connected = status === 'connected'
  return (
    <span
      className={cn('inline-flex items-center gap-1.5 rounded-[var(--radius-full)] px-2.5 py-1 text-[11px] font-semibold', className)}
      style={{
        fontFamily: 'var(--font-mono)',
        letterSpacing: '0.02em',
        color: connected ? 'var(--brand-verified)' : 'var(--brand-text-muted)',
        background: connected ? 'color-mix(in srgb, var(--brand-verified) 14%, transparent)' : 'transparent',
        border: `1px solid ${connected ? 'color-mix(in srgb, var(--brand-verified) 40%, transparent)' : 'var(--brand-border)'}`,
      }}
    >
      <span
        aria-hidden
        className="inline-block h-1.5 w-1.5 rounded-full"
        style={{ background: connected ? 'var(--brand-verified)' : 'var(--brand-text-muted)' }}
      />
      {label}
      {!connected && <span style={{ opacity: 0.75 }}>· próximamente</span>}
    </span>
  )
}
