'use client'

import type { ReactNode } from 'react'
import { usePathname } from 'next/navigation'
import { useMe } from '@/lib/useMe'
import { usePremiumStatus } from '@/lib/usePremiumStatus'
import type { FeatureKey } from '@/lib/api'
import ProUpgradeCard from './ProUpgradeCard'

interface PremiumGateProps {
  feature?: FeatureKey
  children: ReactNode
}

/** Gate declarativo para secciones/páginas enteras (ver auth.md):
 * no logueado → CTA de login; logueado pero sin el plan/entitlement →
 * paywall suave; con acceso → children. El frontend nunca decide el acceso
 * de forma definitiva — esto solo refleja lo que ya validó el backend en
 * cada llamada real (ver src/api/deps.py::require_pro/require_feature). */
export default function PremiumGate({ feature, children }: PremiumGateProps) {
  const pathname = usePathname()
  const { isLoggedIn, isLoading: meLoading } = useMe()
  const { hasAccess, isLoading: statusLoading } = usePremiumStatus()

  if (meLoading) {
    return <div style={{ color: 'var(--muted)', fontSize: 14 }}>Cargando…</div>
  }

  if (!isLoggedIn) {
    return (
      <div style={{
        background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12,
        padding: '56px 20px', textAlign: 'center',
      }}>
        <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text)', marginBottom: 6 }}>
          Inicia sesión para usar funciones premium
        </div>
        <div style={{ fontSize: 13.5, color: 'var(--muted)', marginBottom: 16 }}>
          Guardamos tus alertas, competidores y reportes en tu cuenta.
        </div>
        <a
          href={`/api/auth/login?returnTo=${encodeURIComponent(pathname || '/')}`}
          style={{
            display: 'inline-block', background: 'var(--primary)', color: '#fff', textDecoration: 'none',
            border: 'none', borderRadius: 8, padding: '10px 18px', fontSize: 13.5, fontWeight: 600,
          }}
        >
          Iniciar sesión
        </a>
      </div>
    )
  }

  if (statusLoading) {
    return <div style={{ color: 'var(--muted)', fontSize: 14 }}>Verificando tu plan…</div>
  }

  if (!hasAccess(feature)) {
    return <ProUpgradeCard feature={feature} />
  }

  return <>{children}</>
}
