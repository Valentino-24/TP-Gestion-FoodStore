import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/lib/apiClient'

// ── Types ──────────────────────────────────────────────────────

interface Cliente {
  id: number
  nombre: string
  apellido: string
  email: string
  telefono: string | null
  direccion: string | null
  activo: boolean
}

interface ClienteListResponse {
  items: Cliente[]
  total: number
  page: number
  size: number
  pages: number
}

// ── Component ──────────────────────────────────────────────────

export default function ClientesAdminPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const size = 20

  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin', 'clientes', { page }],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, size }
      const { data } = await apiClient.get<ClienteListResponse>('/clientes/', { params })
      return data
    },
  })

  const clientes = data?.items ?? []
  const total = data?.total ?? 0

  // Simple client-side search filter
  const filtered = search.trim()
    ? clientes.filter(
        (c) =>
          c.nombre.toLowerCase().includes(search.toLowerCase()) ||
          c.apellido.toLowerCase().includes(search.toLowerCase()) ||
          c.email.toLowerCase().includes(search.toLowerCase()),
      )
    : clientes

  const totalPages = Math.ceil(total / size)

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Clientes</h1>
        <input
          className="w-64 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="Buscar por nombre, apellido o email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isError && <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">Error al cargar clientes</div>}

      <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-gray-200 bg-gray-50">
            <tr>
              <th className="px-4 py-3 font-medium text-gray-600">Nombre</th>
              <th className="px-4 py-3 font-medium text-gray-600">Email</th>
              <th className="px-4 py-3 font-medium text-gray-600">Teléfono</th>
              <th className="px-4 py-3 font-medium text-gray-600">Activo</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i}>
                  {Array.from({ length: 4 }).map((_, j) => (
                    <td key={j} className="px-4 py-3"><div className="h-4 w-full animate-pulse rounded bg-gray-100" /></td>
                  ))}
                </tr>
              ))
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-12 text-center text-gray-500">
                  {search ? 'No se encontraron clientes con ese criterio' : 'No hay clientes'}
                </td>
              </tr>
            ) : (
              filtered.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{c.nombre} {c.apellido}</td>
                  <td className="px-4 py-3 text-gray-600">{c.email}</td>
                  <td className="px-4 py-3 text-gray-600">{c.telefono ?? '—'}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${c.activo ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {c.activo ? 'Sí' : 'No'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {!isLoading && totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between text-sm">
          <span className="text-gray-600">Página {page} de {totalPages} ({total} clientes)</span>
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
