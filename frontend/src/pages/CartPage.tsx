import { Link } from 'react-router-dom'
import { useCart } from '@/hooks/useCart'

export default function CartPage() {
  const { items, totalItems, subtotal, removeItem, updateQuantity, clearCart } = useCart()

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <span className="mb-4 text-6xl">🛒</span>
        <h1 className="text-2xl font-bold text-gray-900">Tu carrito está vacío</h1>
        <p className="mt-2 text-gray-500">Agregá productos desde el catálogo para empezar a comprar.</p>
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
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">
          Carrito ({totalItems} {totalItems === 1 ? 'producto' : 'productos'})
        </h1>
        <button
          onClick={clearCart}
          className="text-sm font-medium text-red-600 hover:text-red-700"
        >
          Vaciar carrito
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        {/* Items list */}
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.producto_id}
              className="flex items-center gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
            >
              {/* Image */}
              <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-lg bg-gray-100">
                {item.imagen_url ? (
                  <img
                    src={item.imagen_url}
                    alt={item.producto_nombre}
                    className="h-full w-full rounded-lg object-cover"
                  />
                ) : (
                  <span className="text-2xl">🍽️</span>
                )}
              </div>

              {/* Info */}
              <div className="min-w-0 flex-1">
                <Link
                  to={`/productos/${item.producto_id}`}
                  className="font-semibold text-gray-900 hover:text-blue-600"
                >
                  {item.producto_nombre}
                </Link>
                <p className="mt-0.5 text-sm text-gray-500">
                  ${item.precio_unitario.toFixed(2)} c/u
                </p>
              </div>

              {/* Quantity controls */}
              <div className="flex items-center gap-1">
                <button
                  onClick={() => updateQuantity(item.producto_id, item.cantidad - 1)}
                  className="flex h-8 w-8 items-center justify-center rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-100"
                >
                  −
                </button>
                <span className="w-10 text-center text-sm font-medium text-gray-900">
                  {item.cantidad}
                </span>
                <button
                  onClick={() => updateQuantity(item.producto_id, item.cantidad + 1)}
                  className="flex h-8 w-8 items-center justify-center rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-100"
                >
                  +
                </button>
              </div>

              {/* Line total */}
              <div className="w-24 text-right">
                <p className="font-semibold text-gray-900">
                  ${(item.cantidad * item.precio_unitario).toFixed(2)}
                </p>
              </div>

              {/* Remove */}
              <button
                onClick={() => removeItem(item.producto_id)}
                className="shrink-0 rounded-lg p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600"
                title="Eliminar"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          ))}
        </div>

        {/* Summary sidebar */}
        <div className="h-fit rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">Resumen</h2>
          <div className="mt-4 space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>Subtotal ({totalItems} {totalItems === 1 ? 'producto' : 'productos'})</span>
              <span>${subtotal.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm text-gray-600">
              <span>Envío</span>
              <span className="text-green-600">Gratis</span>
            </div>
            <hr className="my-2" />
            <div className="flex justify-between text-lg font-bold text-gray-900">
              <span>Total</span>
              <span>${subtotal.toFixed(2)}</span>
            </div>
          </div>
          <Link
            to="/checkout"
            className="mt-6 block w-full rounded-lg bg-blue-600 px-4 py-2.5 text-center text-sm font-medium text-white hover:bg-blue-700"
          >
            Ir al checkout
          </Link>
        </div>
      </div>
    </div>
  )
}
