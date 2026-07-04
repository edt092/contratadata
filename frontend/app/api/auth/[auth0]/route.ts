import { handleAuth, handleLogin } from '@auth0/nextjs-auth0'

// GET /api/auth/login, /api/auth/logout, /api/auth/callback, /api/auth/me
// (ver auth.md — SDK oficial de Auth0 para Next.js, Universal Login).
export const GET = handleAuth({
  login: handleLogin({
    authorizationParams: {
      // Sin 'audience' Auth0 no emite un access token válido para NUESTRA
      // API (FastAPI) — solo uno opaco para el propio Auth0. Con audience,
      // el access token es un JWT que src/api/auth0.py puede validar.
      audience: process.env.AUTH0_AUDIENCE,
      scope: 'openid profile email',
    },
  }),
})
