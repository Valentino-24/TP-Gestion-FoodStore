import { useMutation } from '@tanstack/react-query'
import apiClient from '@/lib/apiClient'
import { useAuthStore } from '@/stores/authStore'

// ── Types ───────────────────────────────────────────────────────

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

interface User {
  id: number
  nombre: string
  apellido: string
  email: string
  roles: string[]
}

// ── Hooks ───────────────────────────────────────────────────────

export function useLogin() {
  const hydrate = useAuthStore((state) => state.hydrate)

  return useMutation({
    mutationFn: async (payload: LoginPayload) => {
      await apiClient.post('/auth/login', payload)
      await hydrate()
    },
  })
}

export function useRegister() {
  const hydrate = useAuthStore((state) => state.hydrate)

  return useMutation({
    mutationFn: async (payload: RegisterPayload) => {
      await apiClient.post('/auth/register', payload)
      await hydrate()
    },
  })
}

export function useLogout() {
  const logout = useAuthStore((state) => state.logout)

  return useMutation({
    mutationFn: async () => {
      await logout()
    },
  })
}

export function useCurrentUser() {
  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.get<User>('/auth/me')
      return data
    },
  })
}
