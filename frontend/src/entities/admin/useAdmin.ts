import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/lib/apiClient'
import type { AdminStats, AdminDetailedStats } from '@/shared/types'

// ── Query keys ──────────────────────────────────────────────────

export const adminKeys = {
  stats: ['admin', 'stats'] as const,
  statsDetailed: ['admin', 'stats', 'detailed'] as const,
}

// ── Hooks ───────────────────────────────────────────────────────

export function useAdminStats() {
  return useQuery({
    queryKey: adminKeys.stats,
    queryFn: async () => {
      const { data } = await apiClient.get<AdminStats>('/admin/stats')
      return data
    },
    staleTime: 1000 * 60 * 1, // 1 minuto
  })
}

export function useAdminDetailedStats() {
  return useQuery({
    queryKey: adminKeys.statsDetailed,
    queryFn: async () => {
      const { data } = await apiClient.get<AdminDetailedStats>('/admin/stats/detailed')
      return data
    },
    staleTime: 1000 * 60 * 1,
  })
}

// ── Mutations ───────────────────────────────────────────────────

export function useActualizarStock() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, stock }: { id: number; stock: number }) => {
      const { data } = await apiClient.patch(`/productos/${id}/stock`, { cantidad: stock })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] })
    },
  })
}
