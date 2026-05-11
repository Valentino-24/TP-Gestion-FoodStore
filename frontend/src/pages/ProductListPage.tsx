import { useProducts } from '@/hooks/useProducts'
import ProductGrid from '@/components/ProductGrid'
import Pagination from '@/components/Pagination'
import CategoryFilter from '@/components/CategoryFilter'

export default function ProductListPage() {
  const {
    products,
    total,
    page,
    size,
    loading,
    error,
    setPage,
    setCategoriaId,
    categoriaId,
    refetch,
  } = useProducts()

  return (
    <div>
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Productos</h1>
        <CategoryFilter value={categoriaId} onChange={setCategoriaId} />
      </div>

      {loading && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-64 animate-pulse rounded-xl bg-gray-100" />
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 p-6 text-center">
          <p className="text-red-700">{error}</p>
          <button
            onClick={refetch}
            className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
          >
            Reintentar
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          <ProductGrid products={products} />
          <Pagination
            page={page}
            size={size}
            total={total}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  )
}
