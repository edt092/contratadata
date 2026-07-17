'use client'

import { useEffect, useRef, useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import { api, type CheckoutPlan, type CheckoutResponse } from '@/lib/api'

interface WompiCheckoutButtonProps {
  plan: CheckoutPlan
}

/** Botón real de pago de Wompi (ver auth2.md y src/api/routers/premium.py).
 * Pide la referencia + firma de integridad al backend y monta el script del
 * widget de Wompi, que se auto-reemplaza por su propio botón de pago al
 * cargar — nunca manejamos datos de tarjeta directamente. */
export default function WompiCheckoutButton({ plan }: WompiCheckoutButtonProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const { getToken } = useAuth()
  const [checkout, setCheckout] = useState<CheckoutResponse | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    let cancelled = false

    api.createCheckout(getToken, { plan })
      .then(data => { if (!cancelled) { setCheckout(data); setError(false) } })
      .catch(() => { if (!cancelled) { setCheckout(null); setError(true) } })

    return () => { cancelled = true }
  }, [plan, getToken])

  useEffect(() => {
    if (!checkout || !containerRef.current) return

    containerRef.current.innerHTML = ''
    const form = document.createElement('form')
    const script = document.createElement('script')
    script.src = 'https://checkout.wompi.co/widget.js'
    script.setAttribute('data-render', 'button')
    script.setAttribute('data-public-key', checkout.public_key)
    script.setAttribute('data-currency', checkout.currency)
    script.setAttribute('data-amount-in-cents', String(checkout.amount_in_cents))
    script.setAttribute('data-reference', checkout.reference)
    script.setAttribute('data-signature:integrity', checkout.signature)
    script.setAttribute('data-redirect-url', checkout.redirect_url)
    form.appendChild(script)
    containerRef.current.appendChild(form)
  }, [checkout])

  if (error) {
    return (
      <div style={{ fontSize: 13.5, color: 'var(--danger)' }}>
        No pudimos preparar el pago. Intenta de nuevo en unos minutos.
      </div>
    )
  }

  return (
    <div>
      {!checkout && (
        <div style={{ fontSize: 13.5, color: 'var(--muted)' }}>Preparando pago seguro…</div>
      )}
      <div ref={containerRef} />
    </div>
  )
}
