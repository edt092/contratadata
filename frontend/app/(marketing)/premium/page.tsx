'use client'

import { Suspense, type ReactNode } from 'react'
import { usePathname, useSearchParams } from 'next/navigation'
import { useMe } from '@/lib/useMe'
import { usePremiumStatus } from '@/lib/usePremiumStatus'
import { signInHref } from '@/lib/auth-links'
import WompiCheckoutButton from '@/components/WompiCheckoutButton'
import type { CheckoutPlan } from '@/lib/api'
import Container from '@/components/marketing/Container'
import SectionHeading from '@/components/marketing/SectionHeading'

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

// Montos y lógica de checkout sin cambios respecto a la versión anterior —
// solo se retocó la presentación visual. No tocar sin revisar Wompi.
const PRECIO_MENSUAL = 149_000
const PRECIO_ANUAL = 1_490_000
const PRECIO_ANUAL_SIN_DESCUENTO = PRECIO_MENSUAL * 12
const AHORRO_ANUAL = PRECIO_ANUAL_SIN_DESCUENTO - PRECIO_ANUAL
const EQUIVALENTE_MENSUAL_ANUAL = Math.round(PRECIO_ANUAL / 12)

const FAQ_FACTURACION = [
  { q: '¿Puedo cancelar cuando quiera?', a: 'Sí, no hay permanencia mínima. Tu acceso Pro se mantiene activo hasta el final del período ya pagado.' },
  { q: '¿Qué métodos de pago aceptan?', a: 'El checkout lo procesa Wompi — acepta tarjetas de crédito/débito y otros métodos disponibles en Colombia.' },
  { q: '¿Emiten factura?', a: 'El comprobante de pago lo genera Wompi al momento de la transacción.' },
]

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

  const { isLoggedIn, isLoading: meLoading } = useMe()
  const { status, isLoading: statusLoading } = usePremiumStatus()

  const yaEsPro = !!status?.is_pro
  const loginHref = signInHref(pathname || '/premium')

  let cta: (plan: CheckoutPlan) => ReactNode
  if (meLoading || statusLoading) {
    cta = () => <div style={{ fontSize: 13.5, color: 'var(--brand-text-muted)', textAlign: 'center' }}>Cargando…</div>
  } else if (!isLoggedIn) {
    cta = () => (
      <a
        href={loginHref}
        style={{
          display: 'block', textAlign: 'center', background: 'var(--brand-primary)', color: 'var(--brand-primary-foreground)',
          textDecoration: 'none', border: 'none', borderRadius: 'var(--radius-md)', padding: '12px 18px',
          fontSize: 14, fontWeight: 700,
        }}
      >
        Iniciar sesión para continuar
      </a>
    )
  } else {
    cta = plan => <WompiCheckoutButton plan={plan} />
  }

  return (
    <>
      <Container size="md" className="flex flex-col items-center gap-3 pb-4 pt-16 text-center sm:pt-20">
        <SectionHeading
          align="center"
          eyebrow="Plan Profesional"
          title="ContrataData Pro"
          description="Inteligencia comercial para venderle al Estado colombiano."
        />
        {feature && FEATURE_LABELS[feature] && (
          <p className="text-[13.5px] font-semibold" style={{ color: 'var(--brand-primary)' }}>
            Necesitas Pro para {FEATURE_LABELS[feature]}.
          </p>
        )}
      </Container>

      <Container size="sm" className="flex flex-col gap-10 pb-20 sm:pb-28">
        <ul className="mx-auto flex w-full max-w-md flex-col gap-2.5 text-[14px]" style={{ color: 'var(--brand-text)' }}>
          {BENEFICIOS.map(b => (
            <li key={b} className="flex items-start gap-2.5">
              <span aria-hidden style={{ color: 'var(--brand-primary)' }}>✓</span>
              {b}
            </li>
          ))}
        </ul>

        {yaEsPro ? (
          <div
            className="rounded-[var(--radius-lg)] px-6 py-6 text-center"
            style={{ background: 'var(--brand-surface)', border: '1px solid var(--brand-border)' }}
          >
            <div className="text-[15px] font-bold" style={{ color: 'var(--success)' }}>
              ✓ Ya tienes ContrataData Pro activo
            </div>
          </div>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2">
            <div
              className="flex flex-col rounded-[var(--radius-lg)] p-6"
              style={{ background: 'var(--brand-surface)', border: '1px solid var(--brand-border)' }}
            >
              <div className="mb-3.5 text-[13px] font-bold uppercase" style={{ color: 'var(--brand-text-muted)', letterSpacing: '0.06em' }}>
                Mensual
              </div>
              <div className="mb-6 text-center">
                <div className="text-[30px] font-extrabold" style={{ color: 'var(--brand-text)' }}>
                  {fmtCOP(PRECIO_MENSUAL)}{' '}
                  <span className="text-[15px] font-semibold" style={{ color: 'var(--brand-text-muted)' }}>/mes</span>
                </div>
              </div>
              <div className="mt-auto">{cta('monthly')}</div>
            </div>

            <div
              className="relative flex flex-col rounded-[var(--radius-lg)] p-6"
              style={{ background: 'var(--brand-surface-elevated)', border: '2px solid var(--brand-primary)' }}
            >
              <div
                className="absolute -top-3 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-[var(--radius-full)] px-3 py-1 text-[11px] font-bold"
                style={{ background: 'var(--brand-primary)', color: 'var(--brand-primary-foreground)' }}
              >
                Recomendado
              </div>
              <div className="mb-3.5 text-[13px] font-bold uppercase" style={{ color: 'var(--brand-primary)', letterSpacing: '0.06em' }}>
                Anual
              </div>
              <div className="mb-6 text-center">
                <div className="text-[13px] line-through" style={{ color: 'var(--brand-text-muted)' }}>
                  {fmtCOP(PRECIO_ANUAL_SIN_DESCUENTO)}/año
                </div>
                <div className="text-[30px] font-extrabold" style={{ color: 'var(--brand-text)' }}>
                  {fmtCOP(PRECIO_ANUAL)}{' '}
                  <span className="text-[15px] font-semibold" style={{ color: 'var(--brand-text-muted)' }}>/año</span>
                </div>
                <div className="mt-1 text-[13px]" style={{ color: 'var(--brand-text-muted)' }}>
                  Equivale a {fmtCOP(EQUIVALENTE_MENSUAL_ANUAL)}/mes
                </div>
                <div
                  className="mt-2.5 inline-block rounded-[var(--radius-full)] px-3 py-1 text-[12.5px] font-bold"
                  style={{ background: 'color-mix(in srgb, var(--success) 15%, transparent)', color: 'var(--success)' }}
                >
                  Ahorras {fmtCOP(AHORRO_ANUAL)} · 2 meses gratis
                </div>
              </div>
              <div className="mt-auto">{cta('annual')}</div>
            </div>
          </div>
        )}

        <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-[12.5px]" style={{ color: 'var(--brand-text-muted)' }}>
          <span className="flex items-center gap-1.5">
            <span aria-hidden style={{ color: 'var(--brand-verified)' }}>✓</span> Pago seguro procesado por Wompi
          </span>
          <span className="flex items-center gap-1.5">
            <span aria-hidden style={{ color: 'var(--brand-verified)' }}>✓</span> Sin permanencia mínima
          </span>
        </div>

        <div className="flex flex-col gap-3">
          <h2 className="text-[15px] font-semibold" style={{ color: 'var(--brand-text)' }}>
            Preguntas sobre facturación
          </h2>
          {FAQ_FACTURACION.map(faq => (
            <details
              key={faq.q}
              className="rounded-[var(--radius-md)] px-4 py-3"
              style={{ background: 'var(--brand-surface)', border: '1px solid var(--brand-border)' }}
            >
              <summary className="cursor-pointer text-[13.5px] font-semibold" style={{ color: 'var(--brand-text)' }}>
                {faq.q}
              </summary>
              <p className="mt-2 text-[13px] leading-relaxed" style={{ color: 'var(--brand-text-muted)' }}>
                {faq.a}
              </p>
            </details>
          ))}
        </div>
      </Container>
    </>
  )
}
