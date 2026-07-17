/** URL de sign-in de Clerk con retorno a la página actual (ver auth2.md
 * FASE 3) — centralizado para no repetir el nombre del query param
 * ('redirect_url', el que usa <SignIn />) en cada componente. */
export function signInHref(returnTo: string): string {
  return `/sign-in?redirect_url=${encodeURIComponent(returnTo || '/')}`
}
