/**
 * Tests for LoginPage component.
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import LoginPage from '../LoginPage'

// Mock the auth store
vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(() => ({
    login: vi.fn(),
    isLoading: false,
    error: null,
    clearError: vi.fn(),
  })),
}))

describe('LoginPage', () => {
  it('renders login form with email and password inputs', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    )

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /ingresar/i })).toBeInTheDocument()
  })

  it('renders link to register page', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    )

    expect(screen.getByText(/registrate/i)).toBeInTheDocument()
  })
})
