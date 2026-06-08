/**
 * KDSPage — main Kitchen Display System page.
 *
 * Layout with two columns:
 * - "Por preparar" (CONFIRMADO pedidos)
 * - "En preparación" (EN_PREPARACION pedidos)
 *
 * Handles initial load, SSE connection, empty state, and error state.
 */

import { useCocinaStore } from './cocinaStore'
import { useCocinaSSE } from './useCocinaSSE'
import { OrdenCard } from './OrdenCard'

export function KDSPage() {
  const { pedidos, isLoading, error, sseConnected } = useCocinaStore()

  // Connect to SSE on mount
  useCocinaSSE()

  const pending = pedidos.filter((p) => p.estado === 'CONFIRMADO')
  const preparing = pedidos.filter((p) => p.estado === 'EN_PREPARACION')

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-gray-200 bg-white">
        <h1 className="text-xl font-bold text-gray-900">Display de Cocina</h1>
        <div className="flex items-center gap-2">
          <span
            className={`inline-block w-2 h-2 rounded-full ${
              sseConnected ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
          <span className="text-xs text-gray-500">
            {sseConnected ? 'Tiempo real' : 'Sin conexión en vivo'}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex gap-6 p-6 overflow-auto">
        {/* Column: Por preparar */}
        <div className="flex-1 min-w-0">
          <h2 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
            Por preparar
            <span className="text-sm font-normal text-gray-400">
              ({pending.length})
            </span>
          </h2>
          <div className="space-y-4">
            {pending.map((pedido) => (
              <OrdenCard key={pedido.id} pedido={pedido} />
            ))}
            {pending.length === 0 && !isLoading && (
              <p className="text-gray-400 text-sm text-center py-8">
                No hay pedidos pendientes
              </p>
            )}
          </div>
        </div>

        {/* Column: En preparación */}
        <div className="flex-1 min-w-0">
          <h2 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
            En preparación
            <span className="text-sm font-normal text-gray-400">
              ({preparing.length})
            </span>
          </h2>
          <div className="space-y-4">
            {preparing.map((pedido) => (
              <OrdenCard key={pedido.id} pedido={pedido} />
            ))}
            {preparing.length === 0 && !isLoading && (
              <p className="text-gray-400 text-sm text-center py-8">
                No hay pedidos en preparación
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-white/60 flex items-center justify-center">
          <p className="text-gray-500">Cargando pedidos...</p>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
    </div>
  )
}
