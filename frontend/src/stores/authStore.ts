import { create } from 'zustand'
import apiClient, {
  clearTokens,
  storeTokens,
  getStoredAccessToken,
  getStoredRefreshToken,
} from '@/lib/apiClient'

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

interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
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
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  clearError: () => set({ error: null }),

  login: async (payload: LoginPayload) => {
    set({ isLoading: true, error: null })
    try {
      const { data } = await apiClient.post<AuthResponse>('/auth/login', payload)
      storeTokens(data.access_token, data.refresh_token)
      set({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        isAuthenticated: true,
        isLoading: false,
      })
      // Fetch user data after login
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
      const { data } = await apiClient.post<AuthResponse>('/auth/register', payload)
      storeTokens(data.access_token, data.refresh_token)
      set({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        isAuthenticated: true,
        isLoading: false,
      })
      // Fetch user data after registration
      await get().hydrate()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      set({ error: message, isLoading: false })
      throw new Error(message)
    }
  },

  logout: async () => {
    const refreshToken = get().refreshToken ?? getStoredRefreshToken()
    try {
      if (refreshToken) {
        await apiClient.post('/auth/logout', { refresh_token: refreshToken })
      }
    } catch {
      // Ignore errors — we clear local state regardless
    }
    clearTokens()
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    })
    window.location.href = '/login'
  },

  hydrate: async () => {
    const token = getStoredAccessToken()
    if (!token) {
      set({ isAuthenticated: false, user: null, isLoading: false })
      return
    }

    set({ isLoading: true })
    try {
      const { data } = await apiClient.get<User>('/auth/me')
      set({
        user: data,
        accessToken: token,
        refreshToken: getStoredRefreshToken(),
        isAuthenticated: true,
        isLoading: false,
      })
    } catch {
      // Token invalid or expired — try refresh or force login
      clearTokens()
      set({
        user: null,
        accessToken: null,
        refreshToken: null,
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
