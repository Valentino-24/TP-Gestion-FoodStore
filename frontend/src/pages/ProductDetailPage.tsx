import { useParams, Link } from 'react-router-dom'
import { useProductDetail } from '@/hooks/useProducts'

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>()
  const productId = Number(id)
  const { product, loading, error } = useProductDetail(productId)

  if (loading) {
    return (
      <div className="py-16 text-center">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        <p className="mt-4 text-gray-500">Cargando producto…</p>
      </div>
    )
  }

  if (error || !product) {
    return (
      <div className="py-16 text-center">
        <h2 className="text-2xl font-bold text-gray-900">Producto no encontrado</h2>
        <p className="mt-2 text-gray-600">{error || 'El producto que buscás no existe.'}</p>
        <Link
          to="/productos"
          className="mt-6 inline-block rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Volver al catálogo
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl">
      <Link
        to="/productos"
        className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-500"
      >
        ← Volver al catálogo
      </Link>

      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex flex-col gap-6 sm:flex-row">
          {/* Image */}
          <div className="flex h-48 w-full items-center justify-center rounded-lg bg-gray-100 sm:w-64">
            {product.imagen_url ? (
              <img
                src={product.imagen_url}
                alt={product.nombre}
                className="h-full w-full rounded-lg object-cover"
              />
            ) : (
              <span className="text-6xl">🍽️</span>
            )}
          </div>

          {/* Info */}
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900">{product.nombre}</h1>

            <span className="mt-2 inline-block rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
              Cat. {product.categoria_id}
            </span>

            <p className="mt-4 text-gray-600">
              {product.descripcion || 'Sin descripción disponible.'}
            </p>

            <div className="mt-6 text-3xl font-bold text-gray-900">
              ${product.precio.toFixed(2)}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
