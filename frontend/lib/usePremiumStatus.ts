'use client'

import { useUser } from '@auth0/nextjs-auth0/client'
import { useQuery } from '@tanstack/react-query'
import { api, type FeatureKey } from '@/lib/api'

/** Chequeo liviano de plan — is_pro + entitlements por feature. Separado de
 * useMe() porque varios componentes de gating (PremiumGate, botones) solo
 * necesitan esto, no el perfil completo. */
export function usePremiumStatus() {
  const { user: auth0User, isLoading: authLoading } = useUser()

  const statusQ = useQuery({
    queryKey: ['premium-status', auth0User?.sub],
    queryFn: api.premiumStatus,
    enabled: !!auth0User,
    retry: false,
    staleTime: 30_000,
  })

  const hasAccess = (feature?: FeatureKey): boolean => {
    if (!statusQ.data) return false
    if (statusQ.data.is_pro) return true
    return feature ? statusQ.data.entitlements[feature] : false
  }

  return {
    isLoggedIn: !!auth0User,
    isLoading: authLoading || (!!auth0User && statusQ.isLoading),
    status: statusQ.data,
    hasAccess,
  }
}
