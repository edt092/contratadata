'use client'

import { useAuth, useUser } from '@clerk/nextjs'
import { useQuery } from '@tanstack/react-query'
import { api, type FeatureKey } from '@/lib/api'

/** Chequeo liviano de plan — is_pro + entitlements por feature. Separado de
 * useMe() porque varios componentes de gating (PremiumGate, botones) solo
 * necesitan esto, no el perfil completo. */
export function usePremiumStatus() {
  const { user: clerkUser, isLoaded } = useUser()
  const { getToken } = useAuth()

  const statusQ = useQuery({
    queryKey: ['premium-status', clerkUser?.id],
    queryFn: () => api.premiumStatus(getToken),
    enabled: !!clerkUser,
    retry: false,
    staleTime: 30_000,
  })

  const hasAccess = (feature?: FeatureKey): boolean => {
    if (!statusQ.data) return false
    if (statusQ.data.is_pro) return true
    return feature ? statusQ.data.entitlements[feature] : false
  }

  return {
    isLoggedIn: !!clerkUser,
    isLoading: !isLoaded || (!!clerkUser && statusQ.isLoading),
    status: statusQ.data,
    hasAccess,
  }
}
