import type { Producto } from '@/hooks/useProducts'
import ProductCard from '@/components/ProductCard'

interface Props {
  products: Producto[]
}

export default function ProductGrid({ products }: Props) {
  if (products.length === 0) {
    return (
      <div className="py-16 text-center">
        <p className="text-lg text-gray-500">No hay productos disponibles</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  )
}
