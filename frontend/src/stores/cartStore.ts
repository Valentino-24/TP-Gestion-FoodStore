import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// ── Types ──────────────────────────────────────────────────────

export interface CartItem {
  producto_id: number
  producto_nombre: string
  precio_unitario: number
  cantidad: number
  imagen_url: string | null
}

interface CartState {
  items: CartItem[]
  addItem: (item: Omit<CartItem, 'cantidad'>, quantity?: number) => void
  removeItem: (producto_id: number) => void
  updateQuantity: (producto_id: number, cantidad: number) => void
  clearCart: () => void
}

// ── Derived helpers ────────────────────────────────────────────

export function cartTotalItems(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.cantidad, 0)
}

export function cartSubtotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.cantidad * item.precio_unitario, 0)
}

// ── Store ───────────────────────────────────────────────────────

export const useCartStore = create<CartState>()(
  persist(
    (set) => ({
      items: [],

      addItem: (item, quantity = 1) =>
        set((state) => {
          const existing = state.items.find((i) => i.producto_id === item.producto_id)
          if (existing) {
            return {
              items: state.items.map((i) =>
                i.producto_id === item.producto_id
                  ? { ...i, cantidad: i.cantidad + quantity }
                  : i,
              ),
            }
          }
          return {
            items: [...state.items, { ...item, cantidad: quantity }],
          }
        }),

      removeItem: (producto_id) =>
        set((state) => ({
          items: state.items.filter((i) => i.producto_id !== producto_id),
        })),

      updateQuantity: (producto_id, cantidad) =>
        set((state) => {
          if (cantidad <= 0) {
            return { items: state.items.filter((i) => i.producto_id !== producto_id) }
          }
          return {
            items: state.items.map((i) =>
              i.producto_id === producto_id ? { ...i, cantidad } : i,
            ),
          }
        }),

      clearCart: () => set({ items: [] }),
    }),
    {
      name: 'foodstore-cart',
    },
  ),
)
