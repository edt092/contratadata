import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import Navbar from './Navbar'

const mockUseMe = vi.fn()
const mockUsePremiumStatus = vi.fn()
const mockSignOut = vi.fn()

vi.mock('next/navigation', () => ({
  usePathname: () => '/alertas',
}))
vi.mock('@clerk/nextjs', () => ({
  useClerk: () => ({ signOut: mockSignOut }),
}))
vi.mock('@/lib/useMe', () => ({
  useMe: () => mockUseMe(),
}))
vi.mock('@/lib/usePremiumStatus', () => ({
  usePremiumStatus: () => mockUsePremiumStatus(),
}))

describe('Navbar', () => {
  beforeEach(() => {
    mockUseMe.mockReset()
    mockUsePremiumStatus.mockReset()
    mockSignOut.mockReset()
    mockUsePremiumStatus.mockReturnValue({ status: undefined })
  })

  it('muestra "Ingresar" con retorno a la página actual cuando no hay sesión', () => {
    mockUseMe.mockReturnValue({ clerkUser: null, isLoggedIn: false, isLoading: false })

    render(<Navbar />)

    const link = screen.getByRole('link', { name: 'Ingresar' })
    expect(link).toHaveAttribute('href', '/sign-in?redirect_url=%2Falertas')
  })

  it('muestra el nombre del usuario y cierra sesión vía Clerk al hacer clic', () => {
    mockUseMe.mockReturnValue({
      clerkUser: { fullName: 'Ana Prueba', primaryEmailAddress: { emailAddress: 'ana@example.com' }, imageUrl: null },
      isLoggedIn: true,
      isLoading: false,
    })

    render(<Navbar />)

    expect(screen.getByText('Ana Prueba')).toBeInTheDocument()

    fireEvent.click(screen.getByText('Ana Prueba'))
    fireEvent.click(screen.getByText('Cerrar sesión'))

    expect(mockSignOut).toHaveBeenCalledWith({ redirectUrl: '/' })
  })

  it('no muestra nada de sesión mientras isLoading es true', () => {
    mockUseMe.mockReturnValue({ clerkUser: null, isLoggedIn: false, isLoading: true })

    render(<Navbar />)

    expect(screen.queryByRole('link', { name: 'Ingresar' })).not.toBeInTheDocument()
  })
})
