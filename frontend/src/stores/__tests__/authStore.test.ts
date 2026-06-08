/**
 * Tests for authStore (Zustand).
 *
 * These tests verify the store's state management directly,
 * without mocking API calls. Tokens are managed via httpOnly cookies
 * by the backend, so the store only tracks user state.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'

// Mock apiClient before importing the store
vi.mock('@/lib/apiClient', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

// Mock window.location
const mockLocation = { href: '' }
Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true,
})

import { useAuthStore } from '../authStore'

describe('authStore', () => {
  beforeEach(() => {
    // Reset store state
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    })
    vi.clearAllMocks()
    mockLocation.href = ''
  })

  describe('login', () => {
    it('updates state on success', async () => {
      // Mock both calls: POST /login succeeds, GET /me returns user
      const mockApiClient = (await import('@/lib/apiClient')).default
      ;(mockApiClient.post as any).mockResolvedValue({ data: {} })
      ;(mockApiClient.get as any).mockResolvedValue({
        data: {
          id: 1,
          nombre: 'Test',
          apellido: 'User',
          email: 'test@test.com',
          roles: ['CLIENT'],
        },
      })

      await useAuthStore.getState().login({ email: 'test@test.com', password: 'password123' })

      const state = useAuthStore.getState()
      expect(state.isAuthenticated).toBe(true)
      expect(state.isLoading).toBe(false)
      expect(state.error).toBeNull()
      expect(state.user).not.toBeNull()
      expect(state.user!.email).toBe('test@test.com')
    })

    it('sets error on failure', async () => {
      const mockApiClient = (await import('@/lib/apiClient')).default
      ;(mockApiClient.post as any).mockRejectedValue({
        response: { data: { detail: 'Credenciales invalidas' } },
      })

      await expect(
        useAuthStore.getState().login({ email: 'wrong@test.com', password: 'wrong' })
      ).rejects.toThrow()

      const state = useAuthStore.getState()
      expect(state.isAuthenticated).toBe(false)
      expect(state.isLoading).toBe(false)
      expect(state.error).toBe('Credenciales invalidas')
    })
  })

  describe('register', () => {
    it('updates state on success', async () => {
      const mockApiClient = (await import('@/lib/apiClient')).default
      ;(mockApiClient.post as any).mockResolvedValue({ data: {} })
      ;(mockApiClient.get as any).mockResolvedValue({
        data: {
          id: 2,
          nombre: 'New',
          apellido: 'User',
          email: 'new@test.com',
          roles: ['CLIENT'],
        },
      })

      await useAuthStore.getState().register({
        nombre: 'New',
        apellido: 'User',
        email: 'new@test.com',
        password: 'password123',
      })

      const state = useAuthStore.getState()
      expect(state.isAuthenticated).toBe(true)
      expect(state.isLoading).toBe(false)
      expect(state.user).not.toBeNull()
      expect(state.user!.email).toBe('new@test.com')
    })
  })

  describe('logout', () => {
    it('clears state on logout', async () => {
      // Set authenticated state first
      useAuthStore.setState({
        isAuthenticated: true,
        user: { id: 1, nombre: 'T', apellido: 'U', email: 't@t.com', roles: ['CLIENT'] },
      })

      await useAuthStore.getState().logout()

      const state = useAuthStore.getState()
      expect(state.isAuthenticated).toBe(false)
      expect(state.user).toBeNull()
    })
  })
})
