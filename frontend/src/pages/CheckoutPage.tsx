import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import apiClient from '@/lib/apiClient'
import { useCart } from '@/hooks/useCart'
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

interface PedidoResponse {
  id: number
  total: number
  estado: string
  items: Array<{ id: number; producto_nombre: string; cantidad: number; precio_unitario: number; subtotal: number }>
}

// Hardcoded formas de pago (no hay endpoint público para listarlas)
const FORMAS_PAGO = [
  { id: 1, nombre: 'Tarjeta de crédito' },
  { id: 2, nombre: 'Tarjeta de débito' },
]

// ── Component ──────────────────────────────────────────────────

export default function CheckoutPage() {
  const navigate = useNavigate()
  const { items, totalItems, subtotal, clearCart } = useCart()

  const [addresses, setAddresses] = useState<Direccion[]>([])
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(null)
  const [selectedFormaPagoId, setSelectedFormaPagoId] = useState<number>(1)
  const [showAddressForm, setShowAddressForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load addresses
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    apiClient
      .get<Direccion[]>('/direcciones/')
      .then(({ data }) => {
        if (!cancelled) {
          setAddresses(data)
          if (data.length > 0) setSelectedAddressId(data[0].id)
        }
      })
      .catch(() => {
        if (!cancelled) setError('Error al cargar direcciones')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => { cancelled = true }
  }, [])

  // Redirect if cart is empty
  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <span className="mb-4 text-6xl">🛒</span>
        <h1 className="text-2xl font-bold text-gray-900">No hay items para checkout</h1>
        <p className="mt-2 text-gray-500">Agregá productos al carrito antes de continuar.</p>
        <Link
          to="/carrito"
          className="mt-6 rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
        >
          Ir al carrito
        </Link>
      </div>
    )
  }

  async function handleAddressSubmit(data: AddressFormData) {
    try {
      const res = await apiClient.post<Direccion>('/direcciones/', data)
      const newAddress = res.data
      setAddresses((prev) => [...prev, newAddress])
      setSelectedAddressId(newAddress.id)
      setShowAddressForm(false)
    } catch {
      setError('Error al guardar la dirección')
    }
  }

  async function handlePlaceOrder() {
    if (!selectedAddressId) {
      setError('Seleccioná una dirección de envío')
      return
    }

    setSubmitting(true)
    setError(null)

    try {
      const payload = {
        items: items.map((i) => ({
          producto_id: i.producto_id,
          producto_nombre: i.producto_nombre,
          cantidad: i.cantidad,
          precio_unitario: i.precio_unitario,
        })),
        direccion_id: selectedAddressId,
        forma_pago_id: selectedFormaPagoId,
      }

      const { data } = await apiClient.post<PedidoResponse>('/pedidos/', payload)
      clearCart()
      navigate(`/pago/${data.id}`)
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Error al crear el pedido'
          : 'Error de conexión'
      setError(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const selectedAddress = addresses.find((a) => a.id === selectedAddressId)

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Checkout</h1>

      <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
        {/* Form section */}
        <div className="space-y-6">
          {/* Address */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Dirección de envío</h2>

            {loading ? (
              <div className="h-20 animate-pulse rounded-lg bg-gray-100" />
            ) : showAddressForm ? (
              <AddressForm
                onSubmit={handleAddressSubmit}
                onCancel={() => setShowAddressForm(false)}
              />
            ) : (
              <>
                {addresses.length > 0 ? (
                  <div className="space-y-2">
                    {addresses.map((addr) => (
                      <label
                        key={addr.id}
                        className={`flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition ${
                          selectedAddressId === addr.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <input
                          type="radio"
                          name="direccion"
                          checked={selectedAddressId === addr.id}
                          onChange={() => setSelectedAddressId(addr.id)}
                          className="mt-1"
                        />
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {addr.calle} {addr.numero}
                          </p>
                          <p className="text-sm text-gray-500">
                            {addr.ciudad}, {addr.provincia} — CP {addr.codigo_postal}
                          </p>
                          {addr.telefono_contacto && (
                            <p className="text-xs text-gray-400">Tel: {addr.telefono_contacto}</p>
                          )}
                        </div>
                      </label>
                    ))}
                  </div>
                ) : (
                  <p className="mb-3 text-sm text-gray-500">
                    No tenés direcciones guardadas. Agregá una para continuar.
                  </p>
                )}
                <button
                  onClick={() => setShowAddressForm(true)}
                  className="mt-3 text-sm font-medium text-blue-600 hover:text-blue-700"
                >
                  + Agregar dirección
                </button>
              </>
            )}
          </div>

          {/* Payment method */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Forma de pago</h2>
            <div className="space-y-2">
              {FORMAS_PAGO.map((fp) => (
                <label
                  key={fp.id}
                  className={`flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition ${
                    selectedFormaPagoId === fp.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="forma_pago"
                    checked={selectedFormaPagoId === fp.id}
                    onChange={() => setSelectedFormaPagoId(fp.id)}
                    className="mt-0.5"
                  />
                  <span className="text-sm font-medium text-gray-900">{fp.nombre}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Order summary sidebar */}
        <div className="h-fit rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">Resumen del pedido</h2>

          <div className="mt-4 space-y-3">
            {items.map((item) => (
              <div key={item.producto_id} className="flex justify-between text-sm">
                <span className="text-gray-600">
                  {item.producto_nombre} <span className="text-gray-400">x{item.cantidad}</span>
                </span>
                <span className="font-medium text-gray-900">
                  ${(item.cantidad * item.precio_unitario).toFixed(2)}
                </span>
              </div>
            ))}
          </div>

          <hr className="my-4" />

          <div className="space-y-2 text-sm">
            <div className="flex justify-between text-gray-600">
              <span>Subtotal ({totalItems} {totalItems === 1 ? 'producto' : 'productos'})</span>
              <span>${subtotal.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-gray-600">
              <span>Envío</span>
              <span className="text-green-600">Gratis</span>
            </div>
          </div>

          <hr className="my-4" />

          <div className="flex justify-between text-lg font-bold text-gray-900">
            <span>Total</span>
            <span>${subtotal.toFixed(2)}</span>
          </div>

          {selectedAddress && (
            <div className="mt-3 rounded-lg bg-gray-50 p-3 text-xs text-gray-500">
              <p className="font-medium text-gray-700">Enviar a:</p>
              <p>{selectedAddress.calle} {selectedAddress.numero}</p>
              <p>{selectedAddress.ciudad}, {selectedAddress.provincia}</p>
            </div>
          )}

          {error && (
            <p className="mt-3 text-sm text-red-600">{error}</p>
          )}

          <button
            onClick={handlePlaceOrder}
            disabled={submitting || !selectedAddressId}
            className="mt-6 w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {submitting ? 'Creando pedido...' : 'Realizar pedido'}
          </button>
        </div>
      </div>
    </div>
  )
}
