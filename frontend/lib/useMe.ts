'use client'

import { useUser } from '@auth0/nextjs-auth0/client'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

/** Perfil completo (Auth0 + plan resuelto en Neon) del usuario autenticado.
 * `enabled: !!auth0User` evita pegarle a FastAPI mientras la sesión Auth0
 * todavía está cargando o no hay nadie logueado. */
export function useMe() {
  const { user: auth0User, isLoading: authLoading } = useUser()

  const meQ = useQuery({
    queryKey: ['me', auth0User?.sub],
    queryFn: api.me,
    enabled: !!auth0User,
    retry: false,
    staleTime: 30_000,
  })

  return {
    auth0User,
    isLoggedIn: !!auth0User,
    isLoading: authLoading || (!!auth0User && meQ.isLoading),
    me: meQ.data,
    error: meQ.error,
  }
}
