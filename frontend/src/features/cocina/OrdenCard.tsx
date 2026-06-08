/**
 * OrdenCard — a pedido card in the KDS display.
 *
 * Shows:
 * - Order number
 * - Items with quantities
 * - Exclusions / personalization
 * - Customer notes
 * - Urgency timer
 * - Action buttons (Iniciar preparación / Listo)
 */

import { useState } from 'react'
import apiClient from '@/lib/apiClient'
import { TimerUrgencia } from './TimerUrgencia'
import { useCocinaStore } from './cocinaStore'
import type { PedidoCocina } from './types'

interface OrdenCardProps {
  pedido: PedidoCocina
}

export function OrdenCard({ pedido }: OrdenCardProps) {
  const [isUpdating, setIsUpdating] = useState(false)
  const { removePedido, movePedido } = useCocinaStore()

  const isPending = pedido.estado === 'CONFIRMADO'
  const isPreparing = pedido.estado === 'EN_PREPARACION'

  const handleStartPreparation = async () => {
    setIsUpdating(true)
    try {
      await apiClient.patch(`/pedidos/${pedido.id}/estado`, {
        estado: 'EN_PREPARACION',
      })
      movePedido(pedido.id, 'EN_PREPARACION')
    } catch {
      // Error handled silently — the card stays
    } finally {
      setIsUpdating(false)
    }
  }

  const handleMarkDone = async () => {
    setIsUpdating(true)
    try {
      await apiClient.patch(`/pedidos/${pedido.id}/estado`, {
        estado: 'EN_CAMINO',
      })
      removePedido(pedido.id)
    } catch {
      // Error handled silently — the card stays
    } finally {
      setIsUpdating(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-bold text-gray-900">
          Pedido #{pedido.id}
        </h3>
        <TimerUrgencia kitchenEntryAt={pedido.kitchen_entry_at} />
      </div>

      {/* Items */}
      <ul className="space-y-1 mb-3">
        {pedido.items.map((item, idx) => (
          <li key={idx} className="flex justify-between text-sm text-gray-700">
            <span>
              <span className="font-medium">{item.cantidad}x</span>{' '}
              {item.producto_nombre}
            </span>
            <span className="text-gray-500">${item.subtotal.toFixed(2)}</span>
          </li>
        ))}
      </ul>

      {/* Notes */}
      {pedido.notas && (
        <div className="mb-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
          <span className="font-semibold">Nota:</span> {pedido.notas}
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-2 mt-3">
        {isPending && (
          <button
            onClick={handleStartPreparation}
            disabled={isUpdating}
            className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isUpdating ? 'Actualizando...' : 'Iniciar preparación'}
          </button>
        )}
        {isPreparing && (
          <button
            onClick={handleMarkDone}
            disabled={isUpdating}
            className="flex-1 px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isUpdating ? 'Actualizando...' : 'Listo'}
          </button>
        )}
      </div>
    </div>
  )
}
