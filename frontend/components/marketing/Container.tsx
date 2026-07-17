import type { CSSProperties, ElementType, ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface ContainerProps {
  as?: ElementType
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
  style?: CSSProperties
  children: ReactNode
}

const MAX_WIDTH: Record<NonNullable<ContainerProps['size']>, string> = {
  sm: 'var(--container-sm)',
  md: 'var(--container-md)',
  lg: 'var(--container-lg)',
  xl: 'var(--container-xl)',
}

export default function Container({ as: Tag = 'div', size = 'xl', className, style, children }: ContainerProps) {
  return (
    <Tag
      className={cn('mx-auto w-full px-5 sm:px-8', className)}
      style={{ maxWidth: MAX_WIDTH[size], ...style }}
    >
      {children}
    </Tag>
  )
}
