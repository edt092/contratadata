'use client'

import { Suspense, useState } from 'react'
import { usePathname, useSearchParams } from 'next/navigation'
import { useMe } from '@/lib/useMe'
import { usePremiumStatus } from '@/lib/usePremiumStatus'
import WompiCheckoutButton from '@/components/WompiCheckoutButton'
import type { CheckoutPlan } from '@/lib/api'

const BENEFICIOS = [
  'Alertas guardadas por entidad, contratista o filtro',
  'Monitor de competidores',
  'Reportes Excel/PDF de entidades y contratistas',
  'Acceso anticipado a nuevas funciones',
]

const FEATURE_LABELS: Record<string, string> = {
  saved_alerts: 'guardar esta alerta',
  competitor_monitor: 'seguir este competidor',
  reports: 'exportar este reporte',
}

const PRECIO_MENSUAL = 149_000
const PRECIO_ANUAL = 1_490_000
const PRECIO_ANUAL_SIN_DESCUENTO = PRECIO_MENSUAL * 12
const AHORRO_ANUAL = PRECIO_ANUAL_SIN_DESCUENTO - PRECIO_ANUAL
const EQUIVALENTE_MENSUAL_ANUAL = Math.round(PRECIO_ANUAL / 12)

function fmtCOP(n: number): string {
  return `$${n.toLocaleString('es-CO')}`
}

export default function PremiumPage() {
  return (
    <Suspense fallback={null}>
      <PremiumPageContent />
    </Suspense>
  )
}

function PremiumPageContent() {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const feature = searchParams.get('feature')
  const [plan, setPlan] = useState<CheckoutPlan>('annual')

  const { isLoggedIn, isLoading: meLoading } = useMe()
  const { status, isLoading: statusLoading } = usePremiumStatus()

  const yaEsPro = !!status?.is_pro

  return (
    <main style={{ maxWidth: 720, margin: '0 auto', padding: '32px 28px 80px' }} className="animate-fade">
      <div style={{ marginBottom: 28, textAlign: 'center' }}>
        <h1 style={{ margin: '0 0 8px', fontSize: 32, fontWeight: 800, letterSpacing: '-0.025em', color: 'var(--text)' }}>
          ContrataData Pro
        </h1>
        <p style={{ margin: 0, fontSize: 14.5, color: 'var(--muted)' }}>
          Inteligencia comercial para venderle al Estado colombiano.
        </p>
        {feature && FEATURE_LABELS[feature] && (
          <p style={{ margin: '10px 0 0', fontSize: 13.5, color: 'var(--primary)', fontWeight: 600 }}>
            Necesitas Pro para {FEATURE_LABELS[feature]}.
          </p>
        )}
      </div>

      <ul style={{
        margin: '0 0 28px', padding: '0 0 0 18px', fontSize: 14, color: 'var(--text)', lineHeight: 2,
        maxWidth: 420, marginLeft: 'auto', marginRight: 'auto',
      }}>
        {BENEFICIOS.map(b => <li key={b}>{b}</li>)}
      </ul>

      {yaEsPro ? (
        <div style={{
          background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12,
          padding: '24px 22px', textAlign: 'center',
        }}>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--success)' }}>
            ✓ Ya tienes ContrataData Pro activo
          </div>
        </div>
      ) : (
        <div style={{
          background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12,
          padding: '24px 22px',
        }}>
          <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
            <button
              onClick={() => setPlan('annual')}
              style={{
                flex: 1, padding: '10px 14px', borderRadius: 8, fontSize: 13.5, fontWeight: 700,
                cursor: 'pointer', border: plan === 'annual' ? '2px solid var(--primary)' : '1px solid var(--border)',
                background: plan === 'annual' ? 'var(--primary-weak)' : 'var(--surface2)',
                color: plan === 'annual' ? 'var(--primary)' : 'var(--text)',
              }}
            >
              Anual · Recomendado
            </button>
            <button
              onClick={() => setPlan('monthly')}
              style={{
                flex: 1, padding: '10px 14px', borderRadius: 8, fontSize: 13.5, fontWeight: 700,
                cursor: 'pointer', border: plan === 'monthly' ? '2px solid var(--primary)' : '1px solid var(--border)',
                background: plan === 'monthly' ? 'var(--primary-weak)' : 'var(--surface2)',
                color: plan === 'monthly' ? 'var(--primary)' : 'var(--text)',
              }}
            >
              Mensual
            </button>
          </div>

          {plan === 'annual' ? (
            <div style={{ textAlign: 'center', marginBottom: 20 }}>
              <div style={{ fontSize: 13, color: 'var(--muted)', textDecoration: 'line-through' }}>
                {fmtCOP(PRECIO_ANUAL_SIN_DESCUENTO)}/año
              </div>
              <div style={{ fontSize: 30, fontWeight: 800, color: 'var(--text)' }}>
                {fmtCOP(PRECIO_ANUAL)} <span style={{ fontSize: 15, fontWeight: 600, color: 'var(--muted)' }}>/año</span>
              </div>
              <div style={{ fontSize: 13, color: 'var(--muted)', marginTop: 4 }}>
                Equivale a {fmtCOP(EQUIVALENTE_MENSUAL_ANUAL)}/mes
              </div>
              <div style={{
                display: 'inline-block', marginTop: 10, padding: '4px 12px', borderRadius: 20,
                background: 'rgba(16,185,129,0.15)', color: 'var(--success)', fontSize: 12.5, fontWeight: 700,
              }}>
                Ahorras {fmtCOP(AHORRO_ANUAL)} · 2 meses gratis
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', marginBottom: 20 }}>
              <div style={{ fontSize: 30, fontWeight: 800, color: 'var(--text)' }}>
                {fmtCOP(PRECIO_MENSUAL)} <span style={{ fontSize: 15, fontWeight: 600, color: 'var(--muted)' }}>/mes</span>
              </div>
            </div>
          )}

          {meLoading || statusLoading ? (
            <div style={{ fontSize: 13.5, color: 'var(--muted)', textAlign: 'center' }}>Cargando…</div>
          ) : !isLoggedIn ? (
            <a
              href={`/api/auth/login?returnTo=${encodeURIComponent(pathname || '/premium')}`}
              style={{
                display: 'block', textAlign: 'center', background: 'var(--primary)', color: '#fff',
                textDecoration: 'none', border: 'none', borderRadius: 8, padding: '12px 18px',
                fontSize: 14, fontWeight: 700,
              }}
            >
              Iniciar sesión para continuar
            </a>
          ) : (
            <WompiCheckoutButton plan={plan} />
          )}
        </div>
      )}
    </main>
  )
}
