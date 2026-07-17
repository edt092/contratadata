import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface UseCaseCardProps {
  icon: ReactNode
  title: string
  description: string
  className?: string
}

export default function UseCaseCard({ icon, title, description, className }: UseCaseCardProps) {
  return (
    <div
      className={cn('flex flex-col gap-3 rounded-[var(--radius-lg)] p-5', className)}
      style={{ background: 'var(--brand-surface)', border: '1px solid var(--brand-border)' }}
    >
      <div
        aria-hidden
        className="flex h-9 w-9 items-center justify-center rounded-[var(--radius-md)]"
        style={{ background: 'var(--brand-surface-elevated)', color: 'var(--brand-primary)' }}
      >
        {icon}
      </div>
      <h3 className="text-[15px] font-semibold" style={{ color: 'var(--brand-text)' }}>
        {title}
      </h3>
      <p className="text-[13.5px] leading-relaxed" style={{ color: 'var(--brand-text-muted)' }}>
        {description}
      </p>
    </div>
  )
}
