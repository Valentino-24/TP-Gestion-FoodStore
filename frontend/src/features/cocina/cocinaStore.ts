/**
 * Cocina store — manages the KDS pedido list in real time.
 *
 * The store is updated by:
 * 1. Initial fetch (GET /cocina/pedidos)
 * 2. SSE events (PEDIDO_CONFIRMADO, PEDIDO_EN_PREPARACION, etc.)
 * 3. Manual actions (tomar pedido, marcar listo)
 */

import { create } from 'zustand'
import apiClient from '@/lib/apiClient'
import type { PedidoCocina } from './types'

interface CocinaState {
  /** All pedidos currently visible in the KDS. */
  pedidos: PedidoCocina[]
  /** Loading state for initial fetch. */
  isLoading: boolean
  /** Error message, if any. */
  error: string | null
  /** SSE connection status. */
  sseConnected: boolean

  // Actions
  fetchPedidos: () => Promise<void>
  setPedidos: (pedidos: PedidoCocina[]) => void
  addPedido: (pedido: PedidoCocina) => void
  movePedido: (pedidoId: number, toEstado: 'CONFIRMADO' | 'EN_PREPARACION') => void
  removePedido: (pedidoId: number) => void
  setSSEConnected: (connected: boolean) => void
}

export const useCocinaStore = create<CocinaState>((set, get) => ({
  pedidos: [],
  isLoading: false,
  error: null,
  sseConnected: false,

  fetchPedidos: async () => {
    set({ isLoading: true, error: null })
    try {
      const { data } = await apiClient.get<PedidoCocina[]>('/cocina/pedidos')
      set({ pedidos: data, isLoading: false })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al cargar pedidos'
      set({ error: message, isLoading: false })
    }
  },

  setPedidos: (pedidos) => set({ pedidos }),

  addPedido: (pedido) => {
    const { pedidos } = get()
    // Avoid duplicates
    if (pedidos.some((p) => p.id === pedido.id)) return
    set({ pedidos: [...pedidos, pedido] })
  },

  movePedido: (pedidoId, toEstado) => {
    set((state) => ({
      pedidos: state.pedidos.map((p) =>
        p.id === pedidoId ? { ...p, estado: toEstado } : p,
      ),
    }))
  },

  removePedido: (pedidoId) => {
    set((state) => ({
      pedidos: state.pedidos.filter((p) => p.id !== pedidoId),
    }))
  },

  setSSEConnected: (connected) => set({ sseConnected: connected }),
}))
