import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'
import Eyebrow from './Eyebrow'

interface SectionHeadingProps {
  eyebrow?: ReactNode
  title: ReactNode
  description?: ReactNode
  align?: 'left' | 'center'
  as?: 'h1' | 'h2' | 'h3'
  className?: string
}

export default function SectionHeading({
  eyebrow,
  title,
  description,
  align = 'left',
  as: Tag = 'h2',
  className,
}: SectionHeadingProps) {
  return (
    <div
      className={cn('flex flex-col gap-4', align === 'center' && 'items-center text-center', className)}
    >
      {eyebrow && <Eyebrow>{eyebrow}</Eyebrow>}
      <Tag
        className="max-w-2xl text-[28px] leading-[1.15] sm:text-[36px]"
        style={{
          fontFamily: 'var(--font-serif)',
          fontWeight: 400,
          letterSpacing: '-0.01em',
          color: 'var(--brand-text)',
        }}
      >
        {title}
      </Tag>
      {description && (
        <p
          className="max-w-xl text-[15px] leading-relaxed sm:text-base"
          style={{ color: 'var(--brand-text-muted)' }}
        >
          {description}
        </p>
      )}
    </div>
  )
}
