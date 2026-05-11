import { useEffect, useState } from 'react'
import apiClient from '@/lib/apiClient'

// ── Types ──────────────────────────────────────────────────────

interface Cliente {
  id: number
  nombre: string
  apellido: string
  email: string
  telefono: string | null
}

type PageState = 'loading' | 'not_found' | 'error' | 'loaded'

// ── Component ──────────────────────────────────────────────────

export default function ProfilePage() {
  const [pageState, setPageState] = useState<PageState>('loading')
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [cliente, setCliente] = useState<Cliente | null>(null)

  // Editing state
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({ nombre: '', apellido: '', email: '', telefono: '' })
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; msg: string } | null>(null)

  useEffect(() => {
    loadProfile()
  }, [])

  async function loadProfile() {
    setPageState('loading')
    setErrorMsg(null)
    try {
      const { data } = await apiClient.get<Cliente>('/clientes/me')
      setCliente(data)
      setPageState('loaded')
    } catch (err: any) {
      if (err?.response?.status === 404) {
        setPageState('not_found')
      } else {
        setPageState('error')
        setErrorMsg('Error al cargar el perfil')
      }
    }
  }

  function startEditing() {
    if (!cliente) return
    setForm({
      nombre: cliente.nombre,
      apellido: cliente.apellido,
      email: cliente.email,
      telefono: cliente.telefono ?? '',
    })
    setEditing(true)
    setFeedback(null)
  }

  function cancelEditing() {
    setEditing(false)
    setFeedback(null)
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setFeedback(null)
    try {
      const { data } = await apiClient.put<Cliente>('/clientes/me', form)
      setCliente(data)
      setEditing(false)
      setFeedback({ type: 'success', msg: 'Perfil actualizado correctamente' })
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      if (err?.response?.status === 422 && detail) {
        setFeedback({ type: 'error', msg: detail })
      } else {
        setFeedback({ type: 'error', msg: 'Error al guardar los cambios' })
      }
    } finally {
      setSaving(false)
    }
  }

  // ── Loading skeleton ────────────────────────────────────────

  if (pageState === 'loading') {
    return (
      <div>
        <h1 className="mb-6 text-2xl font-bold text-gray-900">Mi Perfil</h1>
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i}>
              <div className="mb-1 h-3 w-20 animate-pulse rounded bg-gray-200" />
              <div className="h-10 w-full animate-pulse rounded-lg bg-gray-100" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  // ── Not found ───────────────────────────────────────────────

  if (pageState === 'not_found') {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <span className="mb-4 text-6xl">👤</span>
        <h2 className="text-xl font-bold text-gray-900">Sin perfil de cliente</h2>
        <p className="mt-2 max-w-md text-gray-500">
          No tenés un perfil de cliente vinculado a tu usuario. Contactá a un administrador para que
          te asigne uno.
        </p>
      </div>
    )
  }

  // ── Error ───────────────────────────────────────────────────

  if (pageState === 'error') {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <span className="mb-4 text-6xl">⚠️</span>
        <h2 className="text-xl font-bold text-gray-900">Algo salió mal</h2>
        <p className="mt-2 text-gray-500">{errorMsg}</p>
        <button
          onClick={loadProfile}
          className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Reintentar
        </button>
      </div>
    )
  }

  // ── Loaded ──────────────────────────────────────────────────

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Mi Perfil</h1>
        {!editing && (
          <button
            onClick={startEditing}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Editar perfil
          </button>
        )}
      </div>

      {feedback && (
        <div
          className={`mb-4 rounded-lg p-3 text-sm ${
            feedback.type === 'success'
              ? 'bg-green-50 text-green-700'
              : 'bg-red-50 text-red-700'
          }`}
        >
          {feedback.msg}
        </div>
      )}

      {editing ? (
        // ── Edit mode ──────────────────────────────────────────
        <form onSubmit={handleSave} className="max-w-md space-y-4">
          {(['nombre', 'apellido', 'email', 'telefono'] as const).map((field) => (
            <div key={field}>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                {field === 'telefono' ? 'Teléfono' : field.charAt(0).toUpperCase() + field.slice(1)}
              </label>
              <input
                type={field === 'email' ? 'email' : 'text'}
                value={form[field]}
                onChange={(e) => setForm((prev) => ({ ...prev, [field]: e.target.value }))}
                required={field !== 'telefono'}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none"
              />
            </div>
          ))}
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? 'Guardando...' : 'Guardar'}
            </button>
            <button
              type="button"
              onClick={cancelEditing}
              disabled={saving}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
          </div>
        </form>
      ) : (
        // ── Display mode ─────────────────────────────────────
        <div className="max-w-md space-y-4">
          {[
            { label: 'Nombre', value: cliente?.nombre },
            { label: 'Apellido', value: cliente?.apellido },
            { label: 'Email', value: cliente?.email },
            { label: 'Teléfono', value: cliente?.telefono || '—' },
          ].map(({ label, value }) => (
            <div key={label}>
              <p className="text-xs font-medium uppercase tracking-wide text-gray-500">{label}</p>
              <p className="mt-1 text-gray-900">{value}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
