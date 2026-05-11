import { useEffect, useState } from 'react'
import apiClient from '@/lib/apiClient'
import AddressForm, { type AddressFormData } from '@/components/AddressForm'

// ── Types ──────────────────────────────────────────────────────

interface Direccion {
  id: number
  calle: string
  numero: string
  ciudad: string
  provincia: string
  codigo_postal: string
  telefono_contacto: string | null
}

// ── Component ──────────────────────────────────────────────────

export default function AddressesPage() {
  const [addresses, setAddresses] = useState<Direccion[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadAddresses()
  }, [])

  async function loadAddresses() {
    setLoading(true)
    setError(null)
    try {
      const { data } = await apiClient.get<Direccion[]>('/direcciones/')
      setAddresses(data)
    } catch {
      setError('Error al cargar las direcciones')
    } finally {
      setLoading(false)
    }
  }

  function handleAdd() {
    setEditingId(null)
    setShowForm(true)
  }

  function handleEdit(id: number) {
    setEditingId(id)
    setShowForm(true)
  }

  function handleCancel() {
    setShowForm(false)
    setEditingId(null)
  }

  async function handleSubmit(data: AddressFormData) {
    setSaving(true)
    try {
      if (editingId) {
        await apiClient.put(`/direcciones/${editingId}`, data)
      } else {
        await apiClient.post('/direcciones/', data)
      }
      setShowForm(false)
      setEditingId(null)
      await loadAddresses()
    } catch {
      setError('Error al guardar la dirección')
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('¿Eliminar esta dirección?')) return
    try {
      await apiClient.delete(`/direcciones/${id}`)
      setAddresses((prev) => prev.filter((a) => a.id !== id))
    } catch {
      setError('Error al eliminar la dirección')
    }
  }

  const editingAddress = editingId ? addresses.find((a) => a.id === editingId) : null

  if (loading) {
    return (
      <div>
        <h1 className="mb-6 text-2xl font-bold text-gray-900">Mis Direcciones</h1>
        <div className="space-y-3">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="h-24 animate-pulse rounded-xl bg-gray-100" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Mis Direcciones</h1>
        {!showForm && (
          <button
            onClick={handleAdd}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            + Agregar dirección
          </button>
        )}
      </div>

      {error && (
        <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
      )}

      {showForm && (
        <div className="mb-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">
            {editingId ? 'Editar dirección' : 'Nueva dirección'}
          </h2>
          <AddressForm
            initialData={
              editingAddress
                ? {
                    calle: editingAddress.calle,
                    numero: editingAddress.numero,
                    ciudad: editingAddress.ciudad,
                    provincia: editingAddress.provincia,
                    codigo_postal: editingAddress.codigo_postal,
                    telefono_contacto: editingAddress.telefono_contacto ?? '',
                  }
                : undefined
            }
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={saving}
          />
        </div>
      )}

      {!showForm && addresses.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <span className="mb-4 text-6xl">📍</span>
          <h2 className="text-xl font-bold text-gray-900">No tenés direcciones guardadas</h2>
          <p className="mt-2 text-gray-500">Agregá una dirección para poder recibir tus pedidos.</p>
        </div>
      )}

      {!showForm && addresses.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2">
          {addresses.map((addr) => (
            <div
              key={addr.id}
              className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="mb-3">
                <p className="font-medium text-gray-900">
                  {addr.calle} {addr.numero}
                </p>
                <p className="text-sm text-gray-500">
                  {addr.ciudad}, {addr.provincia}
                </p>
                <p className="text-sm text-gray-400">CP: {addr.codigo_postal}</p>
                {addr.telefono_contacto && (
                  <p className="text-sm text-gray-400">Tel: {addr.telefono_contacto}</p>
                )}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleEdit(addr.id)}
                  className="rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(addr.id)}
                  className="rounded-lg border border-red-300 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-50"
                >
                  Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
