import { useCategories } from '@/hooks/useProducts'

interface Props {
  value: number | null
  onChange: (categoriaId: number | null) => void
}

export default function CategoryFilter({ value, onChange }: Props) {
  const { categories, loading } = useCategories()

  return (
    <div className="flex items-center gap-3">
      <label htmlFor="category-filter" className="whitespace-nowrap text-sm font-medium text-gray-700">
        Categoría:
      </label>
      <select
        id="category-filter"
        value={value ?? ''}
        onChange={(e) => {
          const val = e.target.value
          onChange(val === '' ? null : Number(val))
        }}
        className="block w-full max-w-xs rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      >
        <option value="">Todas las categorías</option>
        {!loading &&
          categories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.nombre}
            </option>
          ))}
      </select>
    </div>
  )
}
