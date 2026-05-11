import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import apiClient from '@/lib/apiClient'

// ── Types ──────────────────────────────────────────────────────

interface PagoResponse {
  id: number
  pedido_id: number
  monto: number
  metodo: string
  estado: string
}

interface PedidoResponse {
  id: number
  total: number
  estado: string
  items: Array<{ id: number; producto_nombre: string; cantidad: number; precio_unitario: number; subtotal: number }>
}

type PaymentState = 'idle' | 'processing' | 'success' | 'error'

// ── Component ──────────────────────────────────────────────────

export default function PaymentPage() {
  const { pedidoId } = useParams<{ pedidoId: string }>()
  const [pedido, setPedido] = useState<PedidoResponse | null>(null)
  const [pago, setPago] = useState<PagoResponse | null>(null)
  const [paymentState, setPaymentState] = useState<PaymentState>('idle')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load pedido info on mount
  useEffect(() => {
    if (!pedidoId) return
    let cancelled = false

    apiClient
      .get<PedidoResponse>(`/pedidos/${pedidoId}`)
      .then(({ data }) => {
        if (!cancelled) setPedido(data)
      })
      .catch(() => {
        if (!cancelled) setError('No se pudo cargar la información del pedido')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [pedidoId])

  async function handlePay() {
    if (!pedidoId) return
    setPaymentState('processing')
    setError(null)

    try {
      const { data } = await apiClient.post<PagoResponse>('/pagos/', {
        pedido_id: Number(pedidoId),
      })
      setPago(data)
      setPaymentState(data.estado === 'aprobado' ? 'success' : 'error')
      if (data.estado === 'aprobado') {
        // Refresh pedido to get updated estado (CONFIRMADO)
        const pedidoRes = await apiClient.get<PedidoResponse>(`/pedidos/${pedidoId}`)
        setPedido(pedidoRes.data)
      }
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Error al procesar el pago'
          : 'Error de conexión'
      setError(msg)
      setPaymentState('error')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    )
  }

  if (!pedido) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <h1 className="text-2xl font-bold text-gray-900">Pedido no encontrado</h1>
        <Link to="/pedidos" className="mt-4 text-sm font-medium text-blue-600 hover:text-blue-700">
          Ver mis pedidos
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Pago</h1>

      {/* Order info */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Pedido #{pedido.id}</h2>
          <span className={`rounded-full px-3 py-1 text-xs font-medium ${
            pedido.estado === 'PENDIENTE' ? 'bg-yellow-100 text-yellow-800' :
            pedido.estado === 'CONFIRMADO' ? 'bg-green-100 text-green-800' :
            'bg-blue-100 text-blue-800'
          }`}>
            {pedido.estado}
          </span>
        </div>

        {/* Items */}
        <div className="space-y-2">
          {pedido.items.map((item) => (
            <div key={item.id} className="flex justify-between text-sm">
              <span className="text-gray-600">
                {item.producto_nombre} <span className="text-gray-400">x{item.cantidad}</span>
              </span>
              <span className="font-medium text-gray-900">${item.subtotal.toFixed(2)}</span>
            </div>
          ))}
        </div>

        <hr className="my-4" />

        <div className="flex justify-between text-lg font-bold text-gray-900">
          <span>Total</span>
          <span>${pedido.total.toFixed(2)}</span>
        </div>
      </div>

      {/* Payment section */}
      {paymentState === 'idle' && (
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <p className="mb-4 text-sm text-gray-600">
            Hacé clic en "Pagar ahora" para procesar el pago. En esta versión de demostración, el pago se simulará y se aprobará automáticamente.
          </p>
          <button
            onClick={handlePay}
            className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
          >
            Pagar ahora — ${pedido.total.toFixed(2)}
          </button>
        </div>
      )}

      {paymentState === 'processing' && (
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 text-center shadow-sm">
          <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <p className="text-sm text-gray-600">Procesando el pago...</p>
        </div>
      )}

      {paymentState === 'success' && (
        <div className="mt-6 rounded-xl border border-green-200 bg-green-50 p-6 text-center shadow-sm">
          <span className="mb-2 inline-block text-4xl">✅</span>
          <h2 className="text-lg font-semibold text-green-800">Pago aprobado</h2>
          <p className="mt-1 text-sm text-green-700">
            Tu pedido #{pedido.id} está confirmado. {pago && `Método: ${pago.metodo}`}
          </p>
          <div className="mt-4 flex justify-center gap-3">
            <Link
              to={`/pedidos/${pedido.id}`}
              className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700"
            >
              Ver pedido
            </Link>
            <Link
              to="/productos"
              className="rounded-lg border border-green-300 bg-white px-4 py-2 text-sm font-medium text-green-700 hover:bg-green-100"
            >
              Seguir comprando
            </Link>
          </div>
        </div>
      )}

      {paymentState === 'error' && (
        <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-6 text-center shadow-sm">
          <span className="mb-2 inline-block text-4xl">❌</span>
          <h2 className="text-lg font-semibold text-red-800">Error en el pago</h2>
          {error && <p className="mt-1 text-sm text-red-700">{error}</p>}
          <button
            onClick={handlePay}
            className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
          >
            Reintentar
          </button>
        </div>
      )}

      <div className="mt-6 text-center">
        <Link to="/pedidos" className="text-sm font-medium text-gray-500 hover:text-gray-700">
          Ver todos mis pedidos
        </Link>
      </div>
    </div>
  )
}
