import { getAccessToken } from '@auth0/nextjs-auth0'
import { NextResponse } from 'next/server'

// Expone el access token de la sesión Auth0 (cookie httpOnly del SDK, nunca
// localStorage) a fetches autenticados del cliente hacia FastAPI. Ver
// frontend/lib/api.ts y auth.md — "no guardar tokens en localStorage": esto
// no lo persiste, solo lo entrega en memoria para el request en curso.
export async function GET() {
  try {
    const { accessToken } = await getAccessToken()
    return NextResponse.json({ accessToken: accessToken ?? null })
  } catch {
    return NextResponse.json({ accessToken: null }, { status: 401 })
  }
}
