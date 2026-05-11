import { useCartStore, cartTotalItems, cartSubtotal, type CartItem } from '@/stores/cartStore'

export interface UseCartReturn {
  items: CartItem[]
  totalItems: number
  subtotal: number
  addItem: (item: Omit<CartItem, 'cantidad'>, quantity?: number) => void
  removeItem: (producto_id: number) => void
  updateQuantity: (producto_id: number, cantidad: number) => void
  clearCart: () => void
}

export function useCart(): UseCartReturn {
  const items = useCartStore((s) => s.items)
  const addItem = useCartStore((s) => s.addItem)
  const removeItem = useCartStore((s) => s.removeItem)
  const updateQuantity = useCartStore((s) => s.updateQuantity)
  const clearCart = useCartStore((s) => s.clearCart)

  return {
    items,
    totalItems: cartTotalItems(items),
    subtotal: cartSubtotal(items),
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
  }
}
