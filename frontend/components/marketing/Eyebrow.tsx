import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface EyebrowProps {
  children: ReactNode
  className?: string
}

/** Microetiqueta editorial usada antes de titulares de sección. */
export default function Eyebrow({ children, className }: EyebrowProps) {
  return (
    <span
      className={cn('inline-flex items-center gap-2 text-[11px] font-semibold uppercase', className)}
      style={{
        letterSpacing: '0.12em',
        color: 'var(--brand-primary)',
        fontFamily: 'var(--font-mono)',
      }}
    >
      <span
        aria-hidden
        className="inline-block h-1.5 w-1.5 rounded-full"
        style={{ background: 'var(--brand-primary)' }}
      />
      {children}
    </span>
  )
}
