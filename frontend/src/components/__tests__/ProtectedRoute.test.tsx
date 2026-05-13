/**
 * Tests for ProtectedRoute component.
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import ProtectedRoute from '../ProtectedRoute'

// Mock the auth store
const mockUseAuthStore = vi.fn()
vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => mockUseAuthStore(),
}))

function renderProtectedRoute(initialEntries = ['/protected']) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route path="/protected" element={<div>Protected Content</div>} />
        </Route>
        <Route path="/login" element={<div>Login Page</div>} />
      </Routes>
    </MemoryRouter>
  )
}

describe('ProtectedRoute', () => {
  it('redirects to /login when not authenticated', () => {
    mockUseAuthStore.mockReturnValue({ isAuthenticated: false, isLoading: false })

    renderProtectedRoute()

    // Protected content should not be rendered
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
    // Should have redirected to login
    expect(screen.getByText('Login Page')).toBeInTheDocument()
  })

  it('renders protected content when authenticated', () => {
    mockUseAuthStore.mockReturnValue({ isAuthenticated: true, isLoading: false })

    renderProtectedRoute()

    expect(screen.getByText('Protected Content')).toBeInTheDocument()
  })

  it('shows loading state while checking auth', () => {
    mockUseAuthStore.mockReturnValue({ isAuthenticated: false, isLoading: true })

    renderProtectedRoute()

    // Should show loading and not redirect immediately
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
    expect(screen.queryByText('Login Page')).not.toBeInTheDocument()
  })
})
