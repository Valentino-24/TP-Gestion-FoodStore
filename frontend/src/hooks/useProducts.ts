import { useState, useEffect, useCallback } from 'react'
import apiClient from '@/lib/apiClient'

// ── Types ──────────────────────────────────────────────────────

export interface Producto {
  id: number
  nombre: string
  descripcion: string | null
  precio: number
  categoria_id: number
  imagen_url: string | null
  activo: boolean
  creado_en: string
  actualizado_en: string
}

export interface ProductoListResponse {
  items: Producto[]
  total: number
  page: number
  size: number
}

export interface Categoria {
  id: number
  nombre: string
  descripcion: string | null
  activo: boolean
}

interface UseProductsReturn {
  products: Producto[]
  total: number
  page: number
  size: number
  loading: boolean
  error: string | null
  setPage: (page: number) => void
  setCategoriaId: (id: number | null) => void
  categoriaId: number | null
  refetch: () => void
}

interface UseProductDetailReturn {
  product: Producto | null
  loading: boolean
  error: string | null
}

interface UseCategoriesReturn {
  categories: Categoria[]
  loading: boolean
}

// ── Hook: product list ─────────────────────────────────────────

export function useProducts(pageSize = 12): UseProductsReturn {
  const [products, setProducts] = useState<Producto[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [size] = useState(pageSize)
  const [categoriaId, setCategoriaId] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchProducts = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params: Record<string, string | number> = { page, size }
      if (categoriaId !== null) {
        params.categoria_id = categoriaId
      }
      const { data } = await apiClient.get<ProductoListResponse>('/productos/', { params })
      setProducts(data.items)
      setTotal(data.total)
    } catch (err: unknown) {
      const message = extractError(err)
      setError(message)
      setProducts([])
    } finally {
      setLoading(false)
    }
  }, [page, size, categoriaId])

  useEffect(() => {
    fetchProducts()
  }, [fetchProducts])

  // Reset to page 1 when filter changes
  const handleSetCategoriaId = useCallback((id: number | null) => {
    setCategoriaId(id)
    setPage(1)
  }, [])

  return {
    products,
    total,
    page,
    size,
    loading,
    error,
    setPage,
    setCategoriaId: handleSetCategoriaId,
    categoriaId,
    refetch: fetchProducts,
  }
}

// ── Hook: product detail ───────────────────────────────────────

export function useProductDetail(id: number): UseProductDetailReturn {
  const [product, setProduct] = useState<Producto | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    apiClient
      .get<Producto>(`/productos/${id}`)
      .then(({ data }) => {
        if (!cancelled) setProduct(data)
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(extractError(err))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [id])

  return { product, loading, error }
}

// ── Hook: categories ───────────────────────────────────────────

export function useCategories(): UseCategoriesReturn {
  const [categories, setCategories] = useState<Categoria[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    apiClient
      .get<Categoria[]>('/categorias/')
      .then(({ data }) => {
        if (!cancelled) setCategories(data)
      })
      .catch(() => {
        // Silently fail — categories are non-critical
        if (!cancelled) setCategories([])
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  return { categories, loading }
}

// ── Helpers ────────────────────────────────────────────────────

function extractError(err: unknown): string {
  if (err && typeof err === 'object' && 'response' in err) {
    const axiosErr = err as { response?: { data?: { detail?: string } } }
    if (axiosErr.response?.data?.detail) {
      return axiosErr.response.data.detail
    }
    if (axiosErr.response) {
      return 'Error al cargar los datos'
    }
  }
  return 'Error de conexión con el servidor'
}
