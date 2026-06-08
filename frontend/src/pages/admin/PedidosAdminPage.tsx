import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/lib/apiClient'
import { useCambiarEstadoPedido } from '@/entities/pedido/usePedidos'

// ── Types ──────────────────────────────────────────────────────

interface PedidoRow {
  id: number
  usuario_id: number
  estado: string
  total: number
  creado_en: string
}

interface PedidoListResponse {
  items: PedidoRow[]
  total: number
  page: number
  size: number
  pages: number
}

// ── FSM transitions (mirrors backend app/models/pedido.py) ──────

const ESTADO_TRANSITIONS: Record<string, string[]> = {
  PENDIENTE: ['CONFIRMADO', 'CANCELADO'],
  CONFIRMADO: ['EN_PREPARACION', 'CANCELADO'],
  EN_PREPARACION: ['EN_CAMINO'],
  EN_CAMINO: ['ENTREGADO'],
  ENTREGADO: [],
  CANCELADO: [],
}

const ESTADOS = ['PENDIENTE', 'CONFIRMADO', 'EN_PREPARACION', 'EN_CAMINO', 'ENTREGADO', 'CANCELADO']

const ESTADO_COLORS: Record<string, string> = {
  PENDIENTE: 'bg-yellow-100 text-yellow-800',
  CONFIRMADO: 'bg-blue-100 text-blue-800',
  EN_PREPARACION: 'bg-indigo-100 text-indigo-800',
  EN_CAMINO: 'bg-purple-100 text-purple-800',
  ENTREGADO: 'bg-green-100 text-green-800',
  CANCELADO: 'bg-red-100 text-red-800',
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('es-AR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

// ── Component ──────────────────────────────────────────────────

export default function PedidosAdminPage() {
  const [page, setPage] = useState(1)
  const [estadoFilter, setEstadoFilter] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const size = 20

  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'pedidos', { page, estadoFilter }],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, size }
      if (estadoFilter) params.estado = estadoFilter
      const { data } = await apiClient.get<PedidoListResponse>('/pedidos/', { params })
      return data
    },
  })

  const { mutateAsync: cambiarEstado, isPending: updating } = useCambiarEstadoPedido()

  const pedidos = data?.items ?? []
  const total = data?.total ?? 0

  async function handleTransition(pedidoId: number, targetEstado: string) {
    setError(null)
    try {
      await cambiarEstado({ id: pedidoId, estado: targetEstado })
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Error al actualizar'
          : 'Error de conexión'
      setError(msg)
    }
  }

  const totalPages = Math.ceil(total / size)

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Pedidos</h1>
        <select
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          value={estadoFilter}
          onChange={(e) => { setEstadoFilter(e.target.value); setPage(1) }}
        >
          <option value="">Todos los estados</option>
          {ESTADOS.map((est) => (
            <option key={est} value={est}>{est}</option>
          ))}
        </select>
      </div>

      {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>}

      <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-gray-200 bg-gray-50">
            <tr>
              <th className="px-4 py-3 font-medium text-gray-600">ID</th>
              <th className="px-4 py-3 font-medium text-gray-600">Usuario</th>
              <th className="px-4 py-3 font-medium text-gray-600">Total</th>
              <th className="px-4 py-3 font-medium text-gray-600">Estado</th>
              <th className="px-4 py-3 font-medium text-gray-600">Fecha</th>
              <th className="px-4 py-3 font-medium text-gray-600">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i}>
                  {Array.from({ length: 6 }).map((_, j) => (
                    <td key={j} className="px-4 py-3"><div className="h-4 w-full animate-pulse rounded bg-gray-100" /></td>
                  ))}
                </tr>
              ))
            ) : pedidos.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-12 text-center text-gray-500">No hay pedidos</td>
              </tr>
            ) : (
              pedidos.map((p) => {
                const validTransitions = ESTADO_TRANSITIONS[p.estado] ?? []
                return (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">#{p.id}</td>
                    <td className="px-4 py-3 text-gray-600">#{p.usuario_id}</td>
                    <td className="px-4 py-3 text-gray-900 font-medium">${p.total.toFixed(2)}</td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${ESTADO_COLORS[p.estado] ?? 'bg-gray-100 text-gray-800'}`}>
                        {p.estado}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500 text-xs">{formatDate(p.creado_en)}</td>
                    <td className="px-4 py-3">
                      {validTransitions.length > 0 ? (
                        <select
                          value=""
                          disabled={updating}
                          onChange={(e) => {
                            if (e.target.value) handleTransition(p.id, e.target.value)
                          }}
                          className="rounded-lg border border-gray-300 px-2 py-1 text-xs focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
                        >
                          <option value="">Cambiar a...</option>
                          {validTransitions.map((t) => (
                            <option key={t} value={t}>{t}</option>
                          ))}
                        </select>
                      ) : (
                        <span className="text-xs text-gray-400">Sin acciones</span>
                      )}
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {!isLoading && totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between text-sm">
          <span className="text-gray-600">Página {page} de {totalPages} ({total} pedidos)</span>
          <div className="flex gap-2">
            <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}
              className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50">Anterior</button>
            <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}
              className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50">Siguiente</button>
          </div>
        </div>
      )}
    </div>
  )
}
