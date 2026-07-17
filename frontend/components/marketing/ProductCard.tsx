import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

export type ProductStatus = 'disponible' | 'beta' | 'proximamente'

const STATUS_LABEL: Record<ProductStatus, string> = {
  disponible: 'Disponible',
  beta: 'Beta',
  proximamente: 'Próximamente',
}

interface ProductCardProps {
  name: string
  tagline: string
  example: string
  status: ProductStatus
  accentColor: string
  cta?: ReactNode
  className?: string
}

/** Tarjeta de uno de los tres pilares de producto (Explore/Signal/Ask). El
 * estado (`status`) debe reflejar la realidad — Ask nunca se marca
 * "disponible" mientras no exista. */
export default function ProductCard({ name, tagline, example, status, accentColor, cta, className }: ProductCardProps) {
  return (
    <div
      className={cn('flex flex-col gap-4 rounded-[var(--radius-lg)] p-6', className)}
      style={{ background: 'var(--brand-surface)', border: '1px solid var(--brand-border)' }}
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <span aria-hidden className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: accentColor }} />
          <h3 className="text-[17px] font-semibold" style={{ color: 'var(--brand-text)' }}>
            {name}
          </h3>
        </div>
        <span
          className="rounded-[var(--radius-full)] px-2.5 py-0.5 text-[10.5px] font-semibold uppercase"
          style={{
            fontFamily: 'var(--font-mono)',
            letterSpacing: '0.06em',
            color: status === 'proximamente' ? 'var(--brand-text-muted)' : accentColor,
            background: status === 'proximamente' ? 'transparent' : `color-mix(in srgb, ${accentColor} 15%, transparent)`,
            border: status === 'proximamente' ? '1px solid var(--brand-border)' : 'none',
          }}
        >
          {STATUS_LABEL[status]}
        </span>
      </div>

      <p className="text-[14px] leading-relaxed" style={{ color: 'var(--brand-text-muted)' }}>
        {tagline}
      </p>

      <div
        className="rounded-[var(--radius-md)] px-3.5 py-3 text-[12.5px]"
        style={{ background: 'var(--brand-surface-elevated)', color: 'var(--brand-text-muted)', fontFamily: 'var(--font-mono)' }}
      >
        {example}
      </div>

      {cta && <div className="mt-auto pt-1">{cta}</div>}
    </div>
  )
}
