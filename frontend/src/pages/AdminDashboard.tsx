import { useEffect, useState } from 'react'
import apiClient from '@/lib/apiClient'

// ── Types ──────────────────────────────────────────────────────

interface AdminStats {
  pedidos_hoy: number
  ingresos_hoy: number
  total_productos: number
  total_clientes: number
}

// ── Component ──────────────────────────────────────────────────

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  function loadStats() {
    setLoading(true)
    setError(null)
    apiClient
      .get<AdminStats>('/admin/stats')
      .then(({ data }) => setStats(data))
      .catch(() => setError('Error al cargar las estadísticas'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadStats()
  }, [])

  const cards = [
    {
      label: 'Pedidos hoy',
      value: stats?.pedidos_hoy ?? '-',
      color: 'bg-blue-500',
      loading,
    },
    {
      label: 'Ingresos hoy',
      value: stats ? `$${stats.ingresos_hoy.toLocaleString('es-AR', { minimumFractionDigits: 2 })}` : '-',
      color: 'bg-green-500',
      loading,
    },
    {
      label: 'Productos activos',
      value: stats?.total_productos ?? '-',
      color: 'bg-purple-500',
      loading,
    },
    {
      label: 'Clientes activos',
      value: stats?.total_clientes ?? '-',
      color: 'bg-orange-500',
      loading,
    },
  ]

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        {error && (
          <button
            onClick={loadStats}
            className="rounded-lg bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-700"
          >
            Reintentar
          </button>
        )}
      </div>

      {error && (
        <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
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
              {card.loading ? (
                <div className="mt-2 h-8 w-24 animate-pulse rounded bg-gray-100" />
              ) : (
                <p className="mt-1 text-3xl font-bold text-gray-900">{card.value}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
