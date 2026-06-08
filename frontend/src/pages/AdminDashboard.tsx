import { useAdminStats, useAdminDetailedStats } from '@/entities/admin/useAdmin'
import IngresosChart from '@/shared/ui/IngresosChart'
import PedidosPorEstadoChart from '@/shared/ui/PedidosPorEstadoChart'
import TopProductosChart from '@/shared/ui/TopProductosChart'

export default function AdminDashboard() {
  const { data: stats, isLoading, isError, refetch } = useAdminStats()
  const { data: detailed } = useAdminDetailedStats()

  const cards = [
    {
      label: 'Pedidos hoy',
      value: stats?.pedidos_hoy ?? '-',
      color: 'bg-blue-500',
    },
    {
      label: 'Ingresos hoy',
      value: stats ? `$${stats.ingresos_hoy.toLocaleString('es-AR', { minimumFractionDigits: 2 })}` : '-',
      color: 'bg-green-500',
    },
    {
      label: 'Productos activos',
      value: stats?.total_productos ?? '-',
      color: 'bg-purple-500',
    },
    {
      label: 'Clientes activos',
      value: stats?.total_clientes ?? '-',
      color: 'bg-orange-500',
    },
  ]

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        {isError && (
          <button
            onClick={() => refetch()}
            className="rounded-lg bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-700"
          >
            Reintentar
          </button>
        )}
      </div>

      {isError && (
        <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          Error al cargar las estadísticas
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => (
          <div
            key={card.label}
            className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm"
          >
            <div className={`h-1.5 ${card.color}`} />
            <div className="p-5">
              <p className="text-sm font-medium text-gray-500">{card.label}</p>
              {isLoading ? (
                <div className="mt-2 h-8 w-24 animate-pulse rounded bg-gray-100" />
              ) : (
                <p className="mt-1 text-3xl font-bold text-gray-900">{card.value}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Charts section */}
      {detailed && (
        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <IngresosChart data={detailed.ingresos_por_dia} />
          <PedidosPorEstadoChart data={detailed.pedidos_por_estado} />
          <div className="lg:col-span-2">
            <TopProductosChart data={detailed.top_productos} />
          </div>
        </div>
      )}
    </div>
  )
}
