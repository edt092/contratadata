'use client'

import { useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useClerk } from '@clerk/nextjs'
import { useTheme } from '@/lib/theme-context'
import { useFeedback } from '@/lib/feedback-context'
import { useMe } from '@/lib/useMe'
import { usePremiumStatus } from '@/lib/usePremiumStatus'
import { signInHref } from '@/lib/auth-links'
import { PREMIUM_ENABLED } from '@/lib/featureFlags'

const NAV = [
  { label: 'Explorar', href: '/explorar' },
  { label: 'Sobre el proyecto', href: '/sobre' },
]

const PREMIUM_NAV = [
  { label: 'Premium', href: '/premium' },
  { label: 'Mis alertas', href: '/alertas' },
  { label: 'Competidores', href: '/competidores' },
]

export default function Navbar() {
  const pathname = usePathname()
  const { theme, toggleTheme } = useTheme()
  const { openFeedback } = useFeedback()
  const { clerkUser, isLoggedIn, isLoading } = useMe()
  const { status } = usePremiumStatus()
  const { signOut } = useClerk()
  const [menuOpen, setMenuOpen] = useState(false)

  const isActive = (href: string) =>
    href === '/explorar' ? pathname === '/explorar' || pathname.startsWith('/entidad') || pathname.startsWith('/contratista') : pathname === href

  const loginUrl = signInHref(pathname || '/')

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 60,
      background: 'color-mix(in srgb, var(--surface) 88%, transparent)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border)',
    }}>
      <div style={{
        maxWidth: 'var(--container-xl)',
        margin: '0 auto',
        padding: '0 28px',
        height: 60,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 24,
      }}>
        <Link href="/" style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          textDecoration: 'none',
        }}>
          <Image src="/favicon.svg" alt="ContrataData" width={40} height={27} priority style={{ display: 'block' }} />
          <span style={{
            fontWeight: 800,
            fontSize: 17,
            letterSpacing: '-0.025em',
            color: 'var(--text)',
          }}>
            ContrataData
          </span>
        </Link>

        <nav style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          {[...NAV, ...(PREMIUM_ENABLED ? PREMIUM_NAV : [])].map(item => (
            <Link
              key={item.href}
              href={item.href}
              className="nav-btn"
              style={{ color: isActive(item.href) ? 'var(--primary)' : 'var(--muted)', textDecoration: 'none' }}
            >
              {item.label}
            </Link>
          ))}

          <button
            onClick={openFeedback}
            style={{
              marginLeft: 10,
              background: 'var(--primary-weak)',
              border: '1px solid var(--border)',
              cursor: 'pointer',
              fontSize: 12,
              fontWeight: 600,
              padding: '7px 11px',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--primary)',
            }}
          >
            Feedback
          </button>

          <button
            onClick={toggleTheme}
            aria-label="Cambiar tema"
            style={{
              marginLeft: 10,
              display: 'flex',
              alignItems: 'center',
              gap: 7,
              background: 'var(--surface2)',
              border: '1px solid var(--border)',
              cursor: 'pointer',
              fontSize: 12,
              fontWeight: 600,
              padding: '7px 11px',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--muted)',
            }}
          >
            <span style={{
              width: 11,
              height: 11,
              borderRadius: '50%',
              border: '2px solid currentColor',
              background: theme === 'dark' ? 'transparent' : 'currentColor',
              display: 'block',
            }} />
            {theme === 'dark' ? 'Claro' : 'Oscuro'}
          </button>

          {isLoading ? null : !isLoggedIn ? (
            <a
              href={loginUrl}
              style={{
                marginLeft: 10,
                background: 'linear-gradient(135deg, var(--primary), var(--chart-2))',
                border: 'none',
                cursor: 'pointer',
                fontSize: 12,
                fontWeight: 700,
                padding: '7px 14px',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--on-primary)',
                textDecoration: 'none',
              }}
            >
              Ingresar
            </a>
          ) : (
            <div style={{ position: 'relative', marginLeft: 10 }}>
              <button
                onClick={() => setMenuOpen(o => !o)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  background: 'var(--surface2)', border: '1px solid var(--border)',
                  borderRadius: 'var(--radius-sm)', padding: '5px 10px 5px 5px', cursor: 'pointer',
                }}
              >
                {clerkUser?.imageUrl ? (
                  <img src={clerkUser.imageUrl} alt="" width={22} height={22} style={{ borderRadius: '50%', display: 'block' }} />
                ) : (
                  <span style={{ width: 22, height: 22, borderRadius: '50%', background: 'var(--primary)', display: 'block' }} />
                )}
                <span style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text)', maxWidth: 130, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {clerkUser?.fullName || clerkUser?.primaryEmailAddress?.emailAddress}
                </span>
                {PREMIUM_ENABLED && status?.is_pro && (
                  <span style={{
                    fontSize: 10, fontWeight: 800, letterSpacing: '0.04em', color: 'var(--on-primary)',
                    background: 'linear-gradient(135deg, var(--primary), var(--chart-2))',
                    borderRadius: 'var(--radius-sm)', padding: '2px 6px',
                  }}>
                    PRO
                  </span>
                )}
              </button>

              {menuOpen && (
                <>
                  <div onClick={() => setMenuOpen(false)} style={{ position: 'fixed', inset: 0, zIndex: 90 }} />
                  <div style={{
                    position: 'absolute', top: '110%', right: 0, zIndex: 100,
                    background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
                    boxShadow: 'var(--shadow-md)', overflow: 'hidden', minWidth: 180,
                  }}>
                    <Link
                      href="/cuenta"
                      onClick={() => setMenuOpen(false)}
                      className="row-hover"
                      style={{ display: 'block', padding: '10px 14px', fontSize: 13, color: 'var(--text)', textDecoration: 'none' }}
                    >
                      Mi cuenta
                    </Link>
                    {PREMIUM_ENABLED && status && !status.is_pro && (
                      <Link
                        href="/premium"
                        onClick={() => setMenuOpen(false)}
                        className="row-hover"
                        style={{ display: 'block', padding: '10px 14px', fontSize: 13, color: 'var(--primary)', fontWeight: 600, textDecoration: 'none', borderTop: '1px solid var(--border)' }}
                      >
                        Actualizar a Pro
                      </Link>
                    )}
                    <button
                      onClick={() => signOut({ redirectUrl: '/' })}
                      className="row-hover"
                      style={{
                        display: 'block', width: '100%', textAlign: 'left', background: 'transparent',
                        border: 'none', padding: '10px 14px', fontSize: 13, color: 'var(--danger)',
                        cursor: 'pointer', borderTop: '1px solid var(--border)',
                      }}
                    >
                      Cerrar sesión
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
        </nav>
      </div>
    </header>
  )
}
