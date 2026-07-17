import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useFeatureGate } from './useFeatureGate'

const mockUseMe = vi.fn()
const mockUsePremiumStatus = vi.fn()

vi.mock('next/navigation', () => ({
  usePathname: () => '/alertas',
}))
vi.mock('@/lib/useMe', () => ({
  useMe: () => mockUseMe(),
}))
vi.mock('@/lib/usePremiumStatus', () => ({
  usePremiumStatus: () => mockUsePremiumStatus(),
}))

// No logueado: useFeatureGate redirige con navegación de página completa
// (window.location.href), no con el router de Next — se verifica así.
function setLocationHref() {
  let href = ''
  Object.defineProperty(window, 'location', {
    configurable: true,
    value: { get href() { return href }, set href(v: string) { href = v } },
  })
  return () => href
}

describe('useFeatureGate', () => {
  beforeEach(() => {
    mockUseMe.mockReset()
    mockUsePremiumStatus.mockReset()
  })

  it('redirige a sign-in con retorno a la página actual cuando no está logueado', () => {
    const getHref = setLocationHref()
    mockUseMe.mockReturnValue({ isLoggedIn: false })
    mockUsePremiumStatus.mockReturnValue({ hasAccess: () => false, isLoading: false })

    const { result } = renderHook(() => useFeatureGate('saved_alerts'))
    const onGranted = vi.fn()

    act(() => result.current.attempt(onGranted))

    expect(getHref()).toBe('/sign-in?redirect_url=%2Falertas')
    expect(onGranted).not.toHaveBeenCalled()
  })

  it('abre el paywall inline cuando está logueado pero sin acceso', () => {
    mockUseMe.mockReturnValue({ isLoggedIn: true })
    mockUsePremiumStatus.mockReturnValue({ hasAccess: () => false, isLoading: false })

    const { result } = renderHook(() => useFeatureGate('saved_alerts'))
    const onGranted = vi.fn()

    act(() => result.current.attempt(onGranted))

    expect(result.current.showPaywall).toBe(true)
    expect(onGranted).not.toHaveBeenCalled()
  })

  it('ejecuta la acción directamente cuando está logueado y tiene acceso', () => {
    mockUseMe.mockReturnValue({ isLoggedIn: true })
    mockUsePremiumStatus.mockReturnValue({ hasAccess: () => true, isLoading: false })

    const { result } = renderHook(() => useFeatureGate('saved_alerts'))
    const onGranted = vi.fn()

    act(() => result.current.attempt(onGranted))

    expect(onGranted).toHaveBeenCalledOnce()
    expect(result.current.showPaywall).toBe(false)
  })
})
