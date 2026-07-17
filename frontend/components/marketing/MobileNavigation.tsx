'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import type { ReactNode } from 'react'

export interface MobileNavLink {
  label: string
  href: string
  badge?: string
}

interface MobileNavigationProps {
  open: boolean
  onClose: () => void
  links: MobileNavLink[]
  footer?: ReactNode
}

/** Menú móvil de la landing — overlay a pantalla completa, cierra con
 * Escape, con click fuera y al navegar. Foco visible heredado de
 * `:focus-visible` global (ver app/globals.css). */
export default function MobileNavigation({ open, onClose, links, footer }: MobileNavigationProps) {
  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => {
      window.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [open, onClose])

  if (!open) return null

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Menú de navegación"
      className="fixed inset-0 z-[100] flex flex-col md:hidden"
      style={{ background: 'var(--brand-bg)' }}
    >
      <div className="flex items-center justify-between px-5 py-4" style={{ borderBottom: '1px solid var(--brand-border)' }}>
        <span className="text-[16px] font-extrabold" style={{ color: 'var(--brand-text)' }}>
          ContrataData
        </span>
        <button
          onClick={onClose}
          aria-label="Cerrar menú"
          className="flex h-9 w-9 items-center justify-center rounded-[var(--radius-md)]"
          style={{ color: 'var(--brand-text)', background: 'var(--brand-surface)' }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
            <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </button>
      </div>

      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto px-5 py-6">
        {links.map(link => (
          <Link
            key={link.href}
            href={link.href}
            onClick={onClose}
            className="flex items-center justify-between rounded-[var(--radius-md)] px-3 py-3.5 text-[16px] font-medium"
            style={{ color: 'var(--brand-text)' }}
          >
            {link.label}
            {link.badge && (
              <span className="text-[10.5px] font-semibold uppercase" style={{ color: 'var(--brand-text-muted)' }}>
                {link.badge}
              </span>
            )}
          </Link>
        ))}
      </nav>

      {footer && (
        <div className="px-5 py-5" style={{ borderTop: '1px solid var(--brand-border)' }}>
          {footer}
        </div>
      )}
    </div>
  )
}
