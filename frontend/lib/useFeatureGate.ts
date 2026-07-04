'use client'

import { useState } from 'react'
import { usePathname } from 'next/navigation'
import { useMe } from '@/lib/useMe'
import { usePremiumStatus } from '@/lib/usePremiumStatus'
import type { FeatureKey } from '@/lib/api'

/** Gate imperativo para botones que disparan una acción (Guardar alerta,
 * Seguir competidor, Exportar reporte) en vez de ocultar contenido estático
 * — ver PremiumGate para ese caso. No logueado → redirect a Auth0 Universal
 * Login (con returnTo a la página actual); logueado sin acceso → abre el
 * paywall inline; con acceso → ejecuta la acción real. */
export function useFeatureGate(feature: FeatureKey) {
  const pathname = usePathname()
  const { isLoggedIn } = useMe()
  const { hasAccess, isLoading } = usePremiumStatus()
  const [showPaywall, setShowPaywall] = useState(false)

  const attempt = (onGranted: () => void) => {
    if (!isLoggedIn) {
      window.location.href = `/api/auth/login?returnTo=${encodeURIComponent(pathname || '/')}`
      return
    }
    if (isLoading) return
    if (hasAccess(feature)) {
      onGranted()
    } else {
      setShowPaywall(true)
    }
  }

  return { attempt, feature, showPaywall, closePaywall: () => setShowPaywall(false) }
}
