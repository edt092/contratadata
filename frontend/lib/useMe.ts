'use client'

import { useAuth, useUser } from '@clerk/nextjs'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

/** Perfil completo (Clerk + plan resuelto en Neon) del usuario autenticado.
 * `enabled: !!clerkUser` evita pegarle a FastAPI mientras la sesión de Clerk
 * todavía está cargando o no hay nadie logueado. */
export function useMe() {
  const { user: clerkUser, isLoaded } = useUser()
  const { getToken } = useAuth()

  const meQ = useQuery({
    queryKey: ['me', clerkUser?.id],
    queryFn: () => api.me(getToken),
    enabled: !!clerkUser,
    retry: false,
    staleTime: 30_000,
  })

  return {
    clerkUser,
    isLoggedIn: !!clerkUser,
    isLoading: !isLoaded || (!!clerkUser && meQ.isLoading),
    me: meQ.data,
    error: meQ.error,
  }
}
