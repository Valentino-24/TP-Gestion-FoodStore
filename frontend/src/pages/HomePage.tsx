import { Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useProductosDestacados } from '@/entities/producto/useProductos'
import ProductGrid from '@/components/ProductGrid'

export default function HomePage() {
  const { user } = useAuthStore()
  const { data: products, isLoading, isError } = useProductosDestacados()

  return (
    <div>
      <div className="py-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900">
          Bienvenido, {user?.nombre}!
        </h1>
        <p className="mt-2 text-gray-600">
          Explorá nuestro catálogo de productos o gestioná tu perfil.
        </p>
      </div>

      <div className="mt-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">Productos destacados</h2>
          <Link
            to="/productos"
            className="text-sm font-medium text-blue-600 hover:text-blue-500"
          >
            Ver catálogo completo →
          </Link>
        </div>

        {isLoading && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-56 animate-pulse rounded-xl bg-gray-100" />
            ))}
          </div>
        )}

        {isError && (
          <p className="text-sm text-gray-500">No se pudieron cargar los productos destacados.</p>
        )}

        {!isLoading && !isError && <ProductGrid products={products ?? []} />}
      </div>
    </div>
  )
}
