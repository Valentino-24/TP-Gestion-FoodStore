/** Tipos para el Kitchen Display System (KDS). */

export interface ItemPedidoCocina {
  producto_nombre: string
  cantidad: number
  subtotal: number
  personalizacion?: string | null
}

export interface PedidoCocina {
  id: number
  estado: 'CONFIRMADO' | 'EN_PREPARACION'
  items: ItemPedidoCocina[]
  notas?: string | null
  kitchen_entry_at: string | null
  creado_en: string
}

/** Evento SSE recibido del backend. */
export interface KitchenSSEEvent {
  type: 'PEDIDO_CONFIRMADO' | 'PEDIDO_EN_PREPARACION' | 'PEDIDO_EN_CAMINO' | 'PEDIDO_CANCELADO'
  pedido_id: number
  data: {
    pedido_id: number
    estado: string
    from_state: string
  }
  timestamp: string
}
