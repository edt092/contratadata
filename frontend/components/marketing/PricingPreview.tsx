import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

export interface PricingPlanSummary {
  id: string
  name: string
  price?: string
  priceSuffix?: string
  audience: string
  features: string[]
  cta: ReactNode
  highlighted?: boolean
}

interface PricingPreviewProps {
  plans: PricingPlanSummary[]
  className?: string
}

/** Grilla compacta de planes — usada en la vista previa de la landing y
 * reutilizable en /premium. No decide precios ni IDs de plan: eso lo define
 * quien la use (ver frontend/app/(marketing)/premium/page.tsx). */
export default function PricingPreview({ plans, className }: PricingPreviewProps) {
  return (
    <div className={cn('grid gap-4 sm:grid-cols-2 lg:grid-cols-3', className)}>
      {plans.map(plan => (
        <div
          key={plan.id}
          className="flex flex-col gap-4 rounded-[var(--radius-lg)] p-5"
          style={{
            background: plan.highlighted ? 'var(--brand-surface-elevated)' : 'var(--brand-surface)',
            border: `1px solid ${plan.highlighted ? 'var(--brand-primary)' : 'var(--brand-border)'}`,
          }}
        >
          <div>
            <h3 className="text-[15px] font-semibold" style={{ color: 'var(--brand-text)' }}>
              {plan.name}
            </h3>
            <p className="mt-1 text-[12px]" style={{ color: 'var(--brand-text-muted)' }}>
              {plan.audience}
            </p>
          </div>

          <div>
            {plan.price ? (
              <span className="text-[24px] font-bold" style={{ fontFamily: 'var(--font-mono)', color: 'var(--brand-text)' }}>
                {plan.price}
                {plan.priceSuffix && (
                  <span className="text-[13px] font-medium" style={{ color: 'var(--brand-text-muted)' }}>
                    {' '}{plan.priceSuffix}
                  </span>
                )}
              </span>
            ) : (
              <span className="text-[16px] font-semibold" style={{ color: 'var(--brand-text)' }}>
                Contáctanos
              </span>
            )}
          </div>

          <ul className="flex flex-col gap-2 text-[13px]" style={{ color: 'var(--brand-text-muted)' }}>
            {plan.features.map(f => (
              <li key={f} className="flex items-start gap-2">
                <span aria-hidden style={{ color: 'var(--brand-primary)' }}>✓</span>
                {f}
              </li>
            ))}
          </ul>

          <div className="mt-auto pt-1">{plan.cta}</div>
        </div>
      ))}
    </div>
  )
}
