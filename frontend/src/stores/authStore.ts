/**
 * Auth store — manages authentication state.
 *
 * Tokens are managed as httpOnly cookies by the backend.
 * The store only tracks the authenticated user and UI state.
 */

import { create } from 'zustand'
import apiClient from '@/lib/apiClient'

// ── Types ──────────────────────────────────────────────────────

interface User {
  id: number
  nombre: string
  apellido: string
  email: string
  roles: string[]
}

interface LoginPayload {
  email: string
  password: string
}

interface RegisterPayload {
  nombre: string
  apellido: string
  email: string
  password: string
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (payload: LoginPayload) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  logout: () => Promise<void>
  hydrate: () => Promise<void>
  clearError: () => void
}

// ── Store ───────────────────────────────────────────────────────

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  clearError: () => set({ error: null }),

  login: async (payload: LoginPayload) => {
    set({ isLoading: true, error: null })
    try {
      await apiClient.post('/auth/login', payload)
      // Cookies are set automatically by the backend
      await get().hydrate()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      set({ error: message, isLoading: false })
      throw new Error(message)
    }
  },

  register: async (payload: RegisterPayload) => {
    set({ isLoading: true, error: null })
    try {
      await apiClient.post('/auth/register', payload)
      // Cookies are set automatically by the backend
      await get().hydrate()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      set({ error: message, isLoading: false })
      throw new Error(message)
    }
  },

  logout: async () => {
    try {
      await apiClient.post('/auth/logout')
    } catch {
      // Ignore errors — cookies are cleared regardless
    }
    set({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    })
    window.location.href = '/login'
  },

  hydrate: async () => {
    set({ isLoading: true })
    try {
      const { data } = await apiClient.get<User>('/auth/me')
      set({
        user: data,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      })
    }
  },
}))

// ── Helpers ────────────────────────────────────────────────────

function extractErrorMessage(err: unknown): string {
  if (err && typeof err === 'object' && 'response' in err) {
    const axiosErr = err as {
      response?: { data?: { detail?: string } }
    }
    if (axiosErr.response?.data?.detail) {
      return axiosErr.response.data.detail
    }
  }
  if (err instanceof Error) {
    return err.message
  }
  return 'Ha ocurrido un error inesperado'
}
