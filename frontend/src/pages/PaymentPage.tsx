import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import apiClient from '@/lib/apiClient'
import { useMercadoPago } from '@/hooks/useMercadoPago'
import { usePedido } from '@/entities/pedido/usePedidos'
import { usePaymentStore } from '@/stores/paymentStore'

// ── Types ──────────────────────────────────────────────────────

interface PagoResponse {
  id: number
  pedido_id: number
  monto: number
  metodo: string
  estado: string
  mp_pago_id?: string
  mp_status?: string
}

// ── Component ──────────────────────────────────────────────────

export default function PaymentPage() {
  const { pedidoId } = useParams<{ pedidoId: string }>()
  const [pago, setPago] = useState<PagoResponse | null>(null)
  const [cardNumber, setCardNumber] = useState('')
  const [cardExpiry, setCardExpiry] = useState('')
  const [cardCvv, setCardCvv] = useState('')
  const [cardName, setCardName] = useState('')

  const { createCardToken, status: mpStatus } = useMercadoPago()
  const { data: pedido, isLoading } = usePedido(Number(pedidoId))
  const { status: paymentState, errorDetail, setPaymentStatus, setMpPaymentId, setErrorDetail, resetPayment } = usePaymentStore()

  // Format card number with spaces
  function handleCardNumberChange(value: string) {
    const digits = value.replace(/\D/g, '').slice(0, 16)
    const formatted = digits.replace(/(\d{4})(?=\d)/g, '$1 ')
    setCardNumber(formatted)
  }

  // Format expiry as MM/YYYY
  function handleExpiryChange(value: string) {
    const digits = value.replace(/\D/g, '').slice(0, 6)
    if (digits.length <= 2) {
      setCardExpiry(digits)
    } else if (digits.length <= 4) {
      setCardExpiry(`${digits.slice(0, 2)}/${digits.slice(2)}`)
    } else {
      setCardExpiry(`${digits.slice(0, 2)}/${digits.slice(2, 6)}`)
    }
  }

  async function handlePay() {
    if (!pedidoId || !pedido) return

    setErrorDetail(null)
    setPaymentStatus('processing')

    try {
      // Parse expiry (accepts MM/YY or MM/YYYY)
      const parts = cardExpiry.split('/')
      const month = parts[0]
      let year = parts[1]
      if (!month || !year) throw new Error('Fecha de vencimiento inválida')
      if (year.length === 2) year = '20' + year
      if (year.length !== 4) throw new Error('Fecha de vencimiento inválida')

      // Create card token via MercadoPago
      const token = await createCardToken({
        cardNumber,
        cardExpirationMonth: month,
        cardExpirationYear: year,
        securityCode: cardCvv,
        cardholderName: cardName,
      })

      // Send token to backend
      const { data } = await apiClient.post<PagoResponse>('/pagos/', {
        pedido_id: Number(pedidoId),
        mp_token: token,
      })

      setPago(data)

      if (data.mp_pago_id) {
        setMpPaymentId(data.mp_pago_id)
      }

      if (data.estado === 'aprobado') {
        setPaymentStatus('success')
        // Pedido data already in cache via usePedido hook
      } else {
        setPaymentStatus('error')
        setErrorDetail(
          data.mp_status === 'rejected'
            ? 'El pago fue rechazado. Verificá los datos de la tarjeta e intentá de nuevo.'
            : 'Error al procesar el pago',
        )
      }
    } catch (err: unknown) {
      setPaymentStatus('error')
      const msg =
        err && typeof err === 'object' && 'message' in err
          ? (err as { message: string }).message
          : 'Error al procesar el pago'
      setErrorDetail(msg)
    }
  }

  // ── Render ───────────────────────────────────────────────────

  if (isLoading) {
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

  const isFormValid =
    cardNumber.replace(/\s/g, '').length >= 13 &&
    cardExpiry.length === 5 &&
    cardCvv.length >= 3 &&
    cardName.trim().length > 0

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Pago</h1>

      {/* Order info */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Pedido #{pedido.id}</h2>
          <span
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              pedido.estado === 'PENDIENTE'
                ? 'bg-yellow-100 text-yellow-800'
                : pedido.estado === 'CONFIRMADO'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-blue-100 text-blue-800'
            }`}
          >
            {pedido.estado}
          </span>
        </div>

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

      {/* Card form section */}
      {paymentState === 'idle' && (
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-gray-900">Datos de la tarjeta</h3>

          {mpStatus === 'loading' && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
              Cargando MercadoPago...
            </div>
          )}

          {mpStatus === 'error' && (
            <p className="mb-3 text-sm text-red-600">
              Error al cargar MercadoPago. Verificá la configuración.
            </p>
          )}

          {mpStatus === 'ready' && (
            <form
              onSubmit={(e) => { e.preventDefault(); handlePay() }}
              className="space-y-4"
            >
              {/* Card number */}
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-700">Número de tarjeta</label>
                <input
                  type="text"
                  inputMode="numeric"
                  placeholder="4532 1234 5678 9012"
                  value={cardNumber}
                  onChange={(e) => handleCardNumberChange(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                  required
                />
              </div>

              {/* Name */}
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-700">Titular de la tarjeta</label>
                <input
                  type="text"
                  placeholder="Juan Pérez"
                  value={cardName}
                  onChange={(e) => setCardName(e.target.value.toUpperCase())}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                  required
                />
              </div>

              {/* Expiry + CVV row */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-700">Vencimiento</label>
                  <input
                    type="text"
                    inputMode="numeric"
                    placeholder="MM/AA"
                    value={cardExpiry}
                    onChange={(e) => handleExpiryChange(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-700">CVV</label>
                  <input
                    type="text"
                    inputMode="numeric"
                    placeholder="123"
                    value={cardCvv}
                    onChange={(e) => setCardCvv(e.target.value.replace(/\D/g, '').slice(0, 4))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                    required
                  />
                </div>
              </div>

              {errorDetail && <p className="text-sm text-red-600">{errorDetail}</p>}

              <button
                type="submit"
                disabled={!isFormValid}
                className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              >
                Pagar ${pedido.total.toFixed(2)}
              </button>
            </form>
          )}
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
          {errorDetail && <p className="mt-1 text-sm text-red-700">{errorDetail}</p>}
          <button
            onClick={() => { resetPayment() }}
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
