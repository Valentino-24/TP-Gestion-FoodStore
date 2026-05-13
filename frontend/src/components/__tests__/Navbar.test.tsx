/**
 * Tests for Navbar component.
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Navbar from '../Navbar'

// Mock the auth store
const mockUseAuthStore = vi.fn()
vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => mockUseAuthStore(),
}))

describe('Navbar', () => {
  it('shows user name when authenticated', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: true,
      user: { nombre: 'Juan', apellido: 'Perez', email: 'juan@test.com' },
      logout: vi.fn(),
    })

    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )

    expect(screen.getByText(/juan/i)).toBeInTheDocument()
  })

  it('does not show user name when not authenticated', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      user: null,
      logout: vi.fn(),
    })

    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )

    // When there's no user, the name span is empty — no user info should appear
    expect(screen.queryByText(/juan/i)).not.toBeInTheDocument()
    // Navbar still shows core navigation regardless of auth
    expect(screen.getByText('Mi Perfil')).toBeInTheDocument()
    expect(screen.getByText('Cerrar sesión')).toBeInTheDocument()
  })
})
