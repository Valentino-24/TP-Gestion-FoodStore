import { useParams, Link } from 'react-router-dom'
import apiClient from '@/lib/apiClient'
import { useQuery } from '@tanstack/react-query'
import { usePedido } from '@/entities/pedido/usePedidos'
import type { Direccion } from '@/shared/types'

// ── Helpers ────────────────────────────────────────────────────

const ESTADO_COLORS: Record<string, string> = {
  PENDIENTE: 'bg-yellow-100 text-yellow-800',
  CONFIRMADO: 'bg-blue-100 text-blue-800',
  EN_PREPARACION: 'bg-indigo-100 text-indigo-800',
  EN_CAMINO: 'bg-purple-100 text-purple-800',
  ENTREGADO: 'bg-green-100 text-green-800',
  CANCELADO: 'bg-red-100 text-red-800',
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-AR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// ── Component ──────────────────────────────────────────────────

export default function OrderDetailPage() {
  const { id } = useParams<{ id: string }>()
  const pedidoId = Number(id)
  const { data: pedido, isLoading, isError } = usePedido(pedidoId)

  // Load address separately
  const { data: direccion } = useQuery({
    queryKey: ['direcciones', pedido?.direccion_id],
    queryFn: async () => {
      const { data } = await apiClient.get<Direccion>(`/direcciones/${pedido!.direccion_id}`)
      return data
    },
    enabled: !!pedido?.direccion_id,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    )
  }

  if (isError || !pedido) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <h1 className="text-2xl font-bold text-gray-900">Pedido no encontrado</h1>
        <p className="mt-2 text-gray-500">El pedido que buscás no existe o no te pertenece.</p>
        <Link to="/pedidos" className="mt-6 text-sm font-medium text-blue-600 hover:text-blue-700">
          Volver a mis pedidos
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link to="/pedidos" className="mb-2 inline-block text-sm font-medium text-blue-600 hover:text-blue-700">
            &larr; Mis pedidos
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Pedido #{pedido.id}</h1>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${ESTADO_COLORS[pedido.estado] ?? 'bg-gray-100 text-gray-800'}`}>
          {pedido.estado}
        </span>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        {/* Items */}
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Productos</h2>
          <div className="space-y-3">
            {pedido.items.map((item) => (
              <div key={item.id} className="flex items-center justify-between">
                <div>
                  <Link
                    to={`/productos/${item.producto_id}`}
                    className="font-medium text-gray-900 hover:text-blue-600"
                  >
                    {item.producto_nombre}
                  </Link>
                  <p className="text-sm text-gray-500">
                    ${item.precio_unitario.toFixed(2)} x {item.cantidad}
                  </p>
                </div>
                <p className="font-semibold text-gray-900">${item.subtotal.toFixed(2)}</p>
              </div>
            ))}
          </div>

          <hr className="my-4" />

          <div className="flex justify-between text-lg font-bold text-gray-900">
            <span>Total</span>
            <span>${pedido.total.toFixed(2)}</span>
          </div>
        </div>

        {/* Sidebar info */}
        <div className="space-y-4">
          {/* Address */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-3 text-lg font-semibold text-gray-900">Dirección de envío</h2>
            {direccion ? (
              <div className="text-sm text-gray-600">
                <p className="font-medium text-gray-900">
                  {direccion.calle} {direccion.numero}
                </p>
                <p>{direccion.ciudad}, {direccion.provincia}</p>
                <p>CP {direccion.codigo_postal}</p>
                {direccion.telefono_contacto && (
                  <p className="mt-1 text-gray-500">Tel: {direccion.telefono_contacto}</p>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-400">Sin dirección registrada</p>
            )}
          </div>

          {/* Timeline / estado */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-3 text-lg font-semibold text-gray-900">Estado</h2>
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-3">
                <div className={`h-2.5 w-2.5 rounded-full ${
                  pedido.estado === 'PENDIENTE' ? 'bg-yellow-500' :
                  pedido.estado === 'CONFIRMADO' || pedido.estado === 'EN_PREPARACION' || pedido.estado === 'EN_CAMINO' || pedido.estado === 'ENTREGADO' ? 'bg-green-500' :
                  'bg-red-500'
                }`} />
                <span className="text-gray-600">Estado actual: <strong>{pedido.estado}</strong></span>
              </div>
              <p className="text-gray-400">
                Creado el {formatDate(pedido.creado_en)}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
