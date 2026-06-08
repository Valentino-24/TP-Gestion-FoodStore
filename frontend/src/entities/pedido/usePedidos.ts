import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/lib/apiClient'
import type { Pedido, PedidoListResponse } from '@/shared/types'

// ── Query keys ──────────────────────────────────────────────────

export const pedidoKeys = {
  all: ['pedidos'] as const,
  list: (filters?: Record<string, unknown>) => ['pedidos', 'list', filters] as const,
  detail: (id: number) => ['pedidos', 'detail', id] as const,
}

// ── Hooks: Pedidos ──────────────────────────────────────────────

export function usePedidos(filters?: { page?: number }) {
  const params = new URLSearchParams()
  if (filters?.page) params.set('page', String(filters.page))

  return useQuery({
    queryKey: pedidoKeys.list(filters),
    queryFn: async () => {
      const { data } = await apiClient.get<PedidoListResponse>(`/pedidos/?${params.toString()}`)
      return data
    },
  })
}

export function usePedido(id: number) {
  return useQuery({
    queryKey: pedidoKeys.detail(id),
    queryFn: async () => {
      const { data } = await apiClient.get<Pedido>(`/pedidos/${id}`)
      return data
    },
    enabled: !!id,
  })
}

// ── Mutations: Pedidos ──────────────────────────────────────────

export function useCrearPedido() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: {
      items: Array<{ producto_id: number; producto_nombre: string; cantidad: number; precio_unitario: number }>
      direccion_id: number
      forma_pago_id: number
    }) => {
      const { data } = await apiClient.post<Pedido>('/pedidos/', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pedidoKeys.all })
    },
  })
}

export function useCambiarEstadoPedido() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, estado }: { id: number; estado: string }) => {
      const { data } = await apiClient.patch<Pedido>(`/pedidos/${id}/estado`, { estado })
      return data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: pedidoKeys.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: pedidoKeys.all })
    },
  })
}

export function useCancelarPedido() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await apiClient.patch<Pedido>(`/pedidos/${id}/cancelar`)
      return data
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: pedidoKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: pedidoKeys.all })
    },
  })
}
