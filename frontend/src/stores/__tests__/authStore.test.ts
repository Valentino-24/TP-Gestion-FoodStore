/**
 * Tests for authStore (Zustand).
 *
 * These tests verify the store's state management directly,
 * without mocking API calls.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'

// Mock apiClient before importing the store
vi.mock('@/lib/apiClient', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
  storeTokens: vi.fn(),
  clearTokens: vi.fn(),
  getStoredAccessToken: vi.fn(),
  getStoredRefreshToken: vi.fn(),
}))

// Mock window.location
const mockLocation = { href: '' }
Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true,
})

import { useAuthStore } from '../authStore'
import { storeTokens, clearTokens, getStoredAccessToken, getStoredRefreshToken } from '@/lib/apiClient'

describe('authStore', () => {
  beforeEach(() => {
    // Reset store state
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    })
    vi.clearAllMocks()
    mockLocation.href = ''
    localStorage.clear()
  })

  describe('login', () => {
    it('updates state on success', async () => {
      const mockApiClient = (await import('@/lib/apiClient')).default
      ;(mockApiClient.post as any).mockResolvedValue({
        data: {
          access_token: 'test-access-token',
          refresh_token: 'test-refresh-token',
          token_type: 'bearer',
          expires_in: 1800,
        },
      })
      // Mock hydrate to avoid API call
      const store = useAuthStore.getState()
      vi.spyOn(store, 'hydrate').mockResolvedValue()

      await useAuthStore.getState().login({ email: 'test@test.com', password: 'password123' })

      const state = useAuthStore.getState()
      expect(state.isAuthenticated).toBe(true)
      expect(state.isLoading).toBe(false)
      expect(state.error).toBeNull()
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
      ;(mockApiClient.post as any).mockResolvedValue({
        data: {
          access_token: 'reg-access-token',
          refresh_token: 'reg-refresh-token',
          token_type: 'bearer',
          expires_in: 1800,
        },
      })
      const store = useAuthStore.getState()
      vi.spyOn(store, 'hydrate').mockResolvedValue()

      await useAuthStore.getState().register({
        nombre: 'Test',
        apellido: 'User',
        email: 'new@test.com',
        password: 'password123',
      })

      const state = useAuthStore.getState()
      expect(state.isAuthenticated).toBe(true)
      expect(state.isLoading).toBe(false)
    })
  })

  describe('logout', () => {
    it('clears state on logout', async () => {
      // Set authenticated state first
      useAuthStore.setState({
        isAuthenticated: true,
        accessToken: 'some-token',
        refreshToken: 'some-refresh',
      })

      await useAuthStore.getState().logout()

      const state = useAuthStore.getState()
      expect(state.isAuthenticated).toBe(false)
      expect(state.user).toBeNull()
      expect(state.accessToken).toBeNull()
      expect(state.refreshToken).toBeNull()
    })
  })
})
