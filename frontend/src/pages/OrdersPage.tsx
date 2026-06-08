import { Link } from 'react-router-dom'
import { usePedidos } from '@/entities/pedido/usePedidos'

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

export default function OrdersPage() {
  const { data, isLoading, isError } = usePedidos({ page: 1 })
  const orders = data?.items ?? []

  if (isLoading) {
    return (
      <div className="space-y-3">
        <h1 className="mb-6 text-2xl font-bold text-gray-900">Mis Pedidos</h1>
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-24 animate-pulse rounded-xl bg-gray-100" />
        ))}
      </div>
    )
  }

  if (isError) {
    return (
      <div className="rounded-lg bg-red-50 p-6 text-center">
        <p className="text-red-700">Error al cargar los pedidos</p>
      </div>
    )
  }

  if (orders.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <span className="mb-4 text-6xl">📦</span>
        <h1 className="text-2xl font-bold text-gray-900">No tenés pedidos aún</h1>
        <p className="mt-2 text-gray-500">Explorá el catálogo y hacé tu primer pedido.</p>
        <Link
          to="/productos"
          className="mt-6 rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
        >
          Ver productos
        </Link>
      </div>
    )
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Mis Pedidos</h1>
      <div className="space-y-3">
        {orders.map((order) => (
          <Link
            key={order.id}
            to={`/pedidos/${order.id}`}
            className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition hover:shadow-md"
          >
            <div>
              <p className="font-semibold text-gray-900">
                Pedido #{order.id}
              </p>
              <p className="mt-0.5 text-sm text-gray-500">{formatDate(order.creado_en)}</p>
              <p className="mt-1 text-sm text-gray-500">
                {order.items.length} {order.items.length === 1 ? 'producto' : 'productos'}
              </p>
            </div>
            <div className="text-right">
              <span className={`inline-block rounded-full px-3 py-1 text-xs font-medium ${ESTADO_COLORS[order.estado] ?? 'bg-gray-100 text-gray-800'}`}>
                {order.estado}
              </span>
              <p className="mt-1 text-lg font-bold text-gray-900">
                ${order.total.toFixed(2)}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
