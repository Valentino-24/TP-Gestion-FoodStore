import { useState, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useProductDetail, useCategories } from '@/hooks/useProducts'
import { useCart } from '@/hooks/useCart'

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>()
  const productId = Number(id)
  const { product, loading, error } = useProductDetail(productId)
  const { categories } = useCategories()
  const { addItem } = useCart()

  const [cantidad, setCantidad] = useState(1)
  const [feedback, setFeedback] = useState<'idle' | 'added'>('idle')

  function handleAddToCart() {
    if (!product) return
    addItem(
      {
        producto_id: product.id,
        producto_nombre: product.nombre,
        precio_unitario: product.precio,
        imagen_url: product.imagen_url,
      },
      cantidad,
    )
    setFeedback('added')
    setTimeout(() => setFeedback('idle'), 2000)
  }

  const categoryMap = useMemo(() => {
    const map: Record<number, string> = {}
    for (const cat of categories) {
      map[cat.id] = cat.nombre
    }
    return map
  }, [categories])

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
              {categoryMap[product.categoria_id] ?? `Cat. ${product.categoria_id}`}
            </span>

            <p className="mt-4 text-gray-600">
              {product.descripcion || 'Sin descripción disponible.'}
            </p>

            <div className="mt-6 text-3xl font-bold text-gray-900">
              ${product.precio.toFixed(2)}
            </div>

            {/* Quantity + Add to cart */}
            <div className="mt-6 flex items-center gap-3">
              <div className="flex items-center rounded-lg border border-gray-300">
                <button
                  onClick={() => setCantidad((c) => Math.max(1, c - 1))}
                  className="flex h-10 w-10 items-center justify-center text-gray-600 hover:bg-gray-100"
                >
                  −
                </button>
                <span className="flex h-10 w-12 items-center justify-center text-sm font-medium text-gray-900">
                  {cantidad}
                </span>
                <button
                  onClick={() => setCantidad((c) => c + 1)}
                  className="flex h-10 w-10 items-center justify-center text-gray-600 hover:bg-gray-100"
                >
                  +
                </button>
              </div>

              <button
                onClick={handleAddToCart}
                className={`flex-1 rounded-lg px-4 py-2.5 text-sm font-medium text-white transition ${
                  feedback === 'added'
                    ? 'bg-green-600'
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {feedback === 'added' ? '✓ Agregado' : 'Agregar al carrito'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
