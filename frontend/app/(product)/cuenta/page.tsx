'use client'

import { Suspense, useEffect, useState } from 'react'
import { usePathname, useSearchParams } from 'next/navigation'
import { useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import { useAuth } from '@clerk/nextjs'
import { useMe } from '@/lib/useMe'
import { api } from '@/lib/api'
import { signInHref } from '@/lib/auth-links'
import { PREMIUM_ENABLED } from '@/lib/featureFlags'

const PLAN_LABELS: Record<string, string> = {
  trialing: 'En prueba',
  active: 'Activo',
  past_due: 'Pago pendiente',
  canceled: 'Cancelado',
  expired: 'Expirado',
  none: 'Sin plan',
}

// Confirma la activación de un pago recién completado con Wompi. La fuente
// de verdad es el webhook (ver src/api/routers/webhooks.py), que puede
// tardar unos segundos frente al redirect — por eso se hace polling en vez
// de confiar en que el plan ya cambió al volver.
function CheckoutReturnBanner() {
  const searchParams = useSearchParams()
  const queryClient = useQueryClient()
  const { getToken } = useAuth()
  const isReturn = searchParams.get('checkout') === 'return'

  const [confirming, setConfirming] = useState(isReturn)
  const [timedOut, setTimedOut] = useState(false)

  useEffect(() => {
    if (!isReturn) return
    let tries = 0
    const interval = setInterval(async () => {
      tries += 1
      const status = await api.premiumStatus(getToken).catch(() => null)
      if (status?.is_pro) {
        queryClient.invalidateQueries({ queryKey: ['me'] })
        queryClient.invalidateQueries({ queryKey: ['premium-status'] })
        setConfirming(false)
        clearInterval(interval)
      } else if (tries >= 8) {
        setConfirming(false)
        setTimedOut(true)
        clearInterval(interval)
      }
    }, 2000)
    return () => clearInterval(interval)
  }, [isReturn, queryClient, getToken])

  if (!isReturn || (!confirming && !timedOut)) return null

  return (
    <div style={{
      background: confirming ? 'var(--primary-weak)' : 'rgba(239,68,68,0.12)',
      border: `1px solid ${confirming ? 'var(--primary)' : 'rgba(239,68,68,0.3)'}`,
      borderRadius: 'var(--radius-lg)', padding: '14px 16px', marginBottom: 20, fontSize: 13.5,
      color: confirming ? 'var(--primary)' : 'var(--danger)', fontWeight: 600,
    }}>
      {confirming
        ? 'Confirmando tu pago…'
        : 'Tu pago se está procesando, esto puede tardar un minuto — recarga la página.'}
    </div>
  )
}

export default function CuentaPage() {
  const pathname = usePathname()
  const { clerkUser, isLoggedIn, isLoading, me } = useMe()

  if (isLoading) {
    return (
      <main style={{ maxWidth: 'var(--container-xs)', margin: '0 auto', padding: '32px 28px 80px' }} className="animate-fade">
        <div style={{ color: 'var(--muted)', fontSize: 14 }}>Cargando…</div>
      </main>
    )
  }

  if (!isLoggedIn) {
    return (
      <main style={{ maxWidth: 'var(--container-xs)', margin: '0 auto', padding: '32px 28px 80px' }} className="animate-fade">
        <h1 style={{ margin: '0 0 16px', fontSize: 30, fontWeight: 800, color: 'var(--text)' }}>Mi cuenta</h1>
        <div style={{
          background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-sm)', padding: '56px 20px', textAlign: 'center',
        }}>
          <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text)', marginBottom: 16 }}>
            Inicia sesión para ver tu cuenta
          </div>
          <a
            href={signInHref(pathname || '/cuenta')}
            style={{
              display: 'inline-block', background: 'var(--primary)', color: 'var(--on-primary)', textDecoration: 'none',
              border: 'none', borderRadius: 'var(--radius-sm)', padding: '10px 18px', fontSize: 13.5, fontWeight: 700,
            }}
          >
            Iniciar sesión
          </a>
        </div>
      </main>
    )
  }

  return (
    <main style={{ maxWidth: 640, margin: '0 auto', padding: '32px 28px 80px' }} className="animate-fade">
      <h1 style={{ margin: '0 0 24px', fontSize: 30, fontWeight: 800, color: 'var(--text)' }}>Mi cuenta</h1>

      <Suspense fallback={null}>
        <CheckoutReturnBanner />
      </Suspense>

      <div style={{
        display: 'flex', alignItems: 'center', gap: 14, marginBottom: 20,
        background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-sm)', padding: 18,
      }}>
        {clerkUser?.imageUrl ? (
          <img src={clerkUser.imageUrl} alt="" width={48} height={48} style={{ borderRadius: '50%', display: 'block' }} />
        ) : (
          <span style={{ width: 48, height: 48, borderRadius: '50%', background: 'var(--primary)', display: 'block' }} />
        )}
        <div>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text)' }}>{clerkUser?.fullName}</div>
          <div style={{ fontSize: 13, color: 'var(--muted)' }}>{clerkUser?.primaryEmailAddress?.emailAddress}</div>
        </div>
      </div>

      {PREMIUM_ENABLED && (
        <>
          <div style={{
            background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)',
            boxShadow: 'var(--shadow-sm)', padding: 18, marginBottom: 20,
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          }}>
            <div>
              <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.07em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: 6 }}>
                Plan actual
              </div>
              <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--text)' }}>
                {me?.plan === 'pro' ? 'ContrataData Pro' : 'Free'}
              </div>
            </div>
            <span style={{
              fontSize: 12, fontWeight: 700, padding: '6px 12px', borderRadius: 'var(--radius-sm)',
              color: me?.plan === 'pro' ? 'var(--success)' : 'var(--muted)',
              background: me?.plan === 'pro' ? 'color-mix(in srgb, var(--success) 15%, transparent)' : 'var(--surface2)',
            }}>
              {PLAN_LABELS[me?.premium_status ?? 'none']}
            </span>
          </div>

          {me?.plan !== 'pro' && (
            <Link
              href="/premium"
              style={{
                display: 'inline-block', background: 'var(--primary)', color: 'var(--on-primary)', textDecoration: 'none',
                border: 'none', borderRadius: 'var(--radius-sm)', padding: '10px 18px', fontSize: 13.5, fontWeight: 700,
              }}
            >
              Ver planes y precios
            </Link>
          )}
        </>
      )}
    </main>
  )
}
