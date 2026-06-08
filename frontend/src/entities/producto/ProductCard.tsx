import { Link } from 'react-router-dom'
import { useCart } from '@/hooks/useCart'
import type { Producto } from '@/shared/types'

interface Props {
  product: Producto
  categoria_nombre?: string
}

export default function ProductCard({ product, categoria_nombre }: Props) {
  const { addItem } = useCart()

  function handleAddToCart(e: React.MouseEvent) {
    e.preventDefault()
    e.stopPropagation()
    addItem({
      producto_id: product.id,
      producto_nombre: product.nombre,
      precio_unitario: product.precio,
      imagen_url: product.imagen_url,
    })
  }

  return (
    <Link
      to={`/productos/${product.id}`}
      className="group rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition hover:shadow-md"
    >
      {/* Image placeholder */}
      <div className="mb-3 flex h-40 items-center justify-center rounded-lg bg-gray-100">
        {product.imagen_url ? (
          <img
            src={product.imagen_url}
            alt={product.nombre}
            className="h-full w-full rounded-lg object-cover"
          />
        ) : (
          <span className="text-4xl">🍽️</span>
        )}
      </div>

      <h3 className="font-semibold text-gray-900 group-hover:text-blue-600">
        {product.nombre}
      </h3>

      {product.descripcion && (
        <p className="mt-1 line-clamp-2 text-sm text-gray-500">
          {product.descripcion}
        </p>
      )}

      <div className="mt-3 flex items-center justify-between">
        <span className="text-lg font-bold text-gray-900">
          ${product.precio.toFixed(2)}
        </span>
        <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
          {categoria_nombre ?? `Cat. ${product.categoria_id}`}
        </span>
      </div>

      <button
        onClick={handleAddToCart}
        className="mt-3 w-full rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
      >
        Agregar al carrito
      </button>
    </Link>
  )
}
