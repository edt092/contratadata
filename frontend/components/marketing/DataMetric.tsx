import { cn } from '@/lib/utils'

interface DataMetricProps {
  label: string
  value?: string
  loading?: boolean
  className?: string
}

/** Métrica de confianza (sección "Métricas de confianza" de la landing).
 * Nunca renderiza un número sin `value` real — mientras carga muestra un
 * skeleton, nunca un placeholder inventado. */
export default function DataMetric({ label, value, loading, className }: DataMetricProps) {
  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      {loading || !value ? (
        <div
          aria-hidden
          className="h-8 w-24 animate-pulse rounded-[var(--radius-sm)]"
          style={{ background: 'var(--brand-surface-elevated)' }}
        />
      ) : (
        <span
          className="text-[28px] sm:text-[32px]"
          style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--brand-text)', letterSpacing: '-0.02em' }}
        >
          {value}
        </span>
      )}
      <span className="text-[12.5px]" style={{ color: 'var(--brand-text-muted)' }}>
        {label}
      </span>
    </div>
  )
}
