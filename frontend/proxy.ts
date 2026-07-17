import { clerkMiddleware } from '@clerk/nextjs/server'

// clerkMiddleware() no protege rutas por sí solo — solo habilita el contexto
// de sesión de Clerk (auth(), useAuth()) en toda la app (ver auth2.md FASE
// 3). El gating real de rutas privadas (/alertas, /competidores, /cuenta,
// /premium) se hace del lado del cliente con useMe()/PremiumGate (ver
// frontend/components/PremiumGate.tsx), igual que ya funcionaba con Auth0 —
// la autorización real vive en FastAPI (src/api/deps.py::require_pro), así
// que bloquear en el proxy sería una capa de UX, no de seguridad.
//
// Renombrado de middleware.ts a proxy.ts para Next.js 16 (ver
// https://nextjs.org/docs/messages/middleware-to-proxy). El runtime pasa a
// ser nodejs (proxy no soporta edge), lo cual no afecta a Clerk.
export default clerkMiddleware()

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
}
