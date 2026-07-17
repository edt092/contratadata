'use client'

import { useEffect, useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useClerk } from '@clerk/nextjs'
import { useMe } from '@/lib/useMe'
import { signInHref } from '@/lib/auth-links'
import Container from './Container'
import { PrimaryButton } from './Button'
import MobileNavigation, { type MobileNavLink } from './MobileNavigation'

const NAV_LINKS: MobileNavLink[] = [
  { label: 'Explorar contratos', href: '/explorar' },
  { label: 'Alertas', href: '/alertas' },
  { label: 'Competidores', href: '/competidores' },
  { label: 'Preguntar a ContrataData', href: '/#ask', badge: 'Próximamente' },
  { label: 'Fuentes', href: '/#fuentes' },
  { label: 'Planes', href: '/premium' },
  { label: 'Sobre ContrataData', href: '/sobre' },
]

export default function MarketingHeader() {
  const pathname = usePathname()
  const { clerkUser, isLoggedIn, isLoading } = useMe()
  const { signOut } = useClerk()
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const loginUrl = signInHref(pathname || '/')

  return (
    <>
      <header
        className="sticky top-0 z-50 transition-[background-color,border-color,backdrop-filter] duration-[var(--motion-standard)]"
        style={{
          background: scrolled ? 'color-mix(in srgb, var(--brand-bg) 82%, transparent)' : 'transparent',
          borderBottom: `1px solid ${scrolled ? 'var(--brand-border)' : 'transparent'}`,
          backdropFilter: scrolled ? 'blur(12px)' : 'none',
        }}
      >
        <Container className="flex h-16 items-center justify-between gap-6">
          <Link href="/" className="flex shrink-0 items-center gap-2">
            <Image src="/favicon.svg" alt="" width={28} height={19} priority />
            <span className="text-[16px] font-extrabold" style={{ color: 'var(--brand-text)', letterSpacing: '-0.02em' }}>
              ContrataData
            </span>
          </Link>

          <nav className="hidden items-center gap-1 lg:flex" aria-label="Navegación principal">
            {NAV_LINKS.map(link => (
              <Link
                key={link.href}
                href={link.href}
                className="flex items-center gap-1.5 rounded-[var(--radius-sm)] px-3 py-2 text-[13.5px] font-medium transition-colors"
                style={{ color: 'var(--brand-text-muted)' }}
              >
                {link.label}
                {link.badge && (
                  <span className="text-[9.5px] font-semibold uppercase" style={{ color: 'var(--brand-primary)' }}>
                    {link.badge}
                  </span>
                )}
              </Link>
            ))}
          </nav>

          <div className="hidden items-center gap-3 lg:flex">
            {isLoading ? null : !isLoggedIn ? (
              <>
                <a href={loginUrl} className="text-[13.5px] font-medium" style={{ color: 'var(--brand-text)' }}>
                  Ingresar
                </a>
                <PrimaryButton href="/explorar">Encontrar oportunidades</PrimaryButton>
              </>
            ) : (
              <div className="relative">
                <button
                  onClick={() => setMenuOpen(o => !o)}
                  className="flex items-center gap-2 rounded-[var(--radius-md)] py-1.5 pl-1.5 pr-2.5"
                  style={{ background: 'var(--brand-surface)', border: '1px solid var(--brand-border)' }}
                >
                  {clerkUser?.imageUrl ? (
                    <img src={clerkUser.imageUrl} alt="" width={22} height={22} style={{ borderRadius: '50%' }} />
                  ) : (
                    <span className="block h-[22px] w-[22px] rounded-full" style={{ background: 'var(--brand-primary)' }} />
                  )}
                  <span className="max-w-[120px] truncate text-[12.5px] font-semibold" style={{ color: 'var(--brand-text)' }}>
                    {clerkUser?.fullName || clerkUser?.primaryEmailAddress?.emailAddress}
                  </span>
                </button>

                {menuOpen && (
                  <>
                    <div onClick={() => setMenuOpen(false)} className="fixed inset-0 z-40" />
                    <div
                      className="absolute right-0 top-[calc(100%+8px)] z-50 min-w-[180px] overflow-hidden rounded-[var(--radius-md)]"
                      style={{ background: 'var(--brand-surface)', border: '1px solid var(--brand-border)', boxShadow: 'var(--shadow-md)' }}
                    >
                      <Link
                        href="/explorar"
                        onClick={() => setMenuOpen(false)}
                        className="block px-4 py-2.5 text-[13px]"
                        style={{ color: 'var(--brand-text)' }}
                      >
                        Ir al explorador
                      </Link>
                      <Link
                        href="/cuenta"
                        onClick={() => setMenuOpen(false)}
                        className="block px-4 py-2.5 text-[13px]"
                        style={{ color: 'var(--brand-text)', borderTop: '1px solid var(--brand-border)' }}
                      >
                        Mi cuenta
                      </Link>
                      <button
                        onClick={() => signOut({ redirectUrl: '/' })}
                        className="block w-full px-4 py-2.5 text-left text-[13px]"
                        style={{ color: 'var(--danger)', borderTop: '1px solid var(--brand-border)' }}
                      >
                        Cerrar sesión
                      </button>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>

          <button
            onClick={() => setMobileOpen(true)}
            aria-label="Abrir menú"
            className="flex h-9 w-9 items-center justify-center rounded-[var(--radius-md)] lg:hidden"
            style={{ color: 'var(--brand-text)', background: 'var(--brand-surface)' }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
              <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </Container>
      </header>

      <MobileNavigation
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        links={NAV_LINKS}
        footer={
          isLoggedIn ? (
            <Link href="/cuenta" onClick={() => setMobileOpen(false)} className="text-[14px] font-semibold" style={{ color: 'var(--brand-text)' }}>
              Mi cuenta
            </Link>
          ) : (
            <a href={loginUrl} onClick={() => setMobileOpen(false)} className="text-[14px] font-semibold" style={{ color: 'var(--brand-text)' }}>
              Ingresar
            </a>
          )
        }
      />
    </>
  )
}
