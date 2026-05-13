/**
 * Tests for cartStore (Zustand with persist middleware).
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useCartStore, cartTotalItems, cartSubtotal } from '../cartStore'
import type { CartItem } from '../cartStore'

const sampleItem: CartItem = {
  producto_id: 1,
  producto_nombre: 'Test Product',
  precio_unitario: 10.50,
  cantidad: 1,
  imagen_url: null,
}

describe('cartStore', () => {
  beforeEach(() => {
    // Clear the store
    useCartStore.getState().clearCart()
    localStorage.clear()
  })

  describe('addItem', () => {
    it('adds item to empty cart', () => {
      useCartStore.getState().addItem(sampleItem)
      const items = useCartStore.getState().items
      expect(items).toHaveLength(1)
      expect(items[0].producto_nombre).toBe('Test Product')
    })

    it('increments quantity when adding duplicate item', () => {
      useCartStore.getState().addItem(sampleItem)
      useCartStore.getState().addItem(sampleItem)

      const items = useCartStore.getState().items
      expect(items).toHaveLength(1)
      expect(items[0].cantidad).toBe(2)
    })

    it('accepts custom quantity', () => {
      useCartStore.getState().addItem(sampleItem, 3)
      const items = useCartStore.getState().items
      expect(items[0].cantidad).toBe(3)
    })
  })

  describe('removeItem', () => {
    it('removes item by product_id', () => {
      useCartStore.getState().addItem(sampleItem)
      useCartStore.getState().addItem({
        producto_id: 2,
        producto_nombre: 'Other',
        precio_unitario: 5.0,
        imagen_url: null,
      })

      useCartStore.getState().removeItem(1)
      const items = useCartStore.getState().items
      expect(items).toHaveLength(1)
      expect(items[0].producto_id).toBe(2)
    })
  })

  describe('updateQuantity', () => {
    it('updates quantity of existing item', () => {
      useCartStore.getState().addItem(sampleItem)
      useCartStore.getState().updateQuantity(1, 5)

      const items = useCartStore.getState().items
      expect(items[0].cantidad).toBe(5)
    })

    it('removes item when quantity is 0', () => {
      useCartStore.getState().addItem(sampleItem)
      useCartStore.getState().updateQuantity(1, 0)

      expect(useCartStore.getState().items).toHaveLength(0)
    })

    it('removes item when quantity is negative', () => {
      useCartStore.getState().addItem(sampleItem)
      useCartStore.getState().updateQuantity(1, -1)

      expect(useCartStore.getState().items).toHaveLength(0)
    })
  })

  describe('clearCart', () => {
    it('clears all items', () => {
      useCartStore.getState().addItem(sampleItem)
      useCartStore.getState().addItem({
        producto_id: 2,
        producto_nombre: 'Other',
        precio_unitario: 5.0,
        imagen_url: null,
      })

      useCartStore.getState().clearCart()
      expect(useCartStore.getState().items).toHaveLength(0)
    })
  })
})

describe('cart helpers', () => {
  it('cartTotalItems sums quantities', () => {
    const items: CartItem[] = [
      { ...sampleItem, cantidad: 2 },
      { producto_id: 2, producto_nombre: 'P2', precio_unitario: 5.0, cantidad: 3, imagen_url: null },
    ]
    expect(cartTotalItems(items)).toBe(5)
  })

  it('cartSubtotal calculates correctly', () => {
    const items: CartItem[] = [
      { ...sampleItem, cantidad: 2 },
      { producto_id: 2, producto_nombre: 'P2', precio_unitario: 5.0, cantidad: 3, imagen_url: null },
    ]
    // 2 * 10.50 + 3 * 5.00 = 21.00 + 15.00 = 36.00
    expect(cartSubtotal(items)).toBe(36.00)
  })

  it('cartSubtotal returns 0 for empty cart', () => {
    expect(cartSubtotal([])).toBe(0)
  })
})
