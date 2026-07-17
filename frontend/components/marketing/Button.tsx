import type { AnchorHTMLAttributes, ButtonHTMLAttributes, CSSProperties, ReactNode } from 'react'
import Link from 'next/link'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonStyles = cva(
  'inline-flex items-center justify-center gap-2 rounded-[var(--radius-md)] text-[14px] font-semibold whitespace-nowrap transition-[transform,opacity,background-color] duration-[var(--motion-fast)] ease-[var(--ease-standard)] disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]',
  {
    variants: {
      size: {
        md: 'h-11 px-5',
        lg: 'h-12 px-6 text-[15px]',
      },
    },
    defaultVariants: { size: 'md' },
  },
)

type Size = VariantProps<typeof buttonStyles>['size']

interface CommonProps {
  children: ReactNode
  className?: string
  size?: Size
}

type ButtonProps =
  | (CommonProps & { href: string } & Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href' | 'className'>)
  | (CommonProps & { href?: undefined } & Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className'>)

type Variant = 'primary' | 'secondary'

const VARIANT_STYLE: Record<Variant, CSSProperties> = {
  primary: { background: 'var(--brand-primary)', color: 'var(--brand-primary-foreground)' },
  secondary: {
    background: 'transparent',
    color: 'var(--brand-text)',
    border: '1px solid var(--brand-border)',
  },
}

function BrandButton({ children, className, size, href, variant, ...rest }: ButtonProps & { variant: Variant }) {
  const cls = cn(buttonStyles({ size }), className)
  const style = VARIANT_STYLE[variant]

  if (href) {
    return (
      <Link href={href} className={cls} style={style} {...(rest as AnchorHTMLAttributes<HTMLAnchorElement>)}>
        {children}
      </Link>
    )
  }
  return (
    <button className={cls} style={style} {...(rest as ButtonHTMLAttributes<HTMLButtonElement>)}>
      {children}
    </button>
  )
}

export function PrimaryButton(props: ButtonProps) {
  return <BrandButton {...props} variant="primary" />
}

export function SecondaryButton(props: ButtonProps) {
  return <BrandButton {...props} variant="secondary" />
}
