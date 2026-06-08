import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/lib/apiClient'
import type { Producto, ProductoListResponse, Categoria } from '@/shared/types'

// ── Query keys ──────────────────────────────────────────────────

export const productoKeys = {
  all: ['productos'] as const,
  list: (filters?: Record<string, unknown>) => ['productos', 'list', filters] as const,
  detail: (id: number) => ['productos', 'detail', id] as const,
}

export const categoriaKeys = {
  all: ['categorias'] as const,
  list: () => ['categorias', 'list'] as const,
}

// ── Hooks: Productos ────────────────────────────────────────────

export function useProductos(filters?: { page?: number; size?: number; categoria_id?: number; search?: string }) {
  const params = new URLSearchParams()
  if (filters?.page) params.set('page', String(filters.page))
  if (filters?.size) params.set('size', String(filters.size))
  if (filters?.categoria_id) params.set('categoria_id', String(filters.categoria_id))
  if (filters?.search) params.set('search', filters.search)

  return useQuery({
    queryKey: productoKeys.list(filters),
    queryFn: async () => {
      const { data } = await apiClient.get<ProductoListResponse>(`/productos/?${params.toString()}`)
      return data
    },
  })
}

export function useProducto(id: number) {
  return useQuery({
    queryKey: productoKeys.detail(id),
    queryFn: async () => {
      const { data } = await apiClient.get<Producto>(`/productos/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useProductosDestacados() {
  return useQuery({
    queryKey: ['productos', 'destacados'],
    queryFn: async () => {
      const { data } = await apiClient.get<ProductoListResponse>('/productos/?size=8')
      return data.items
    },
  })
}

// ── Hooks: Categorías ───────────────────────────────────────────

export function useCategorias() {
  return useQuery({
    queryKey: categoriaKeys.list(),
    queryFn: async () => {
      const { data } = await apiClient.get<Categoria[]>('/categorias/')
      return data
    },
  })
}

// ── Mutations: Productos (admin) ────────────────────────────────

export function useCrearProducto() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: Partial<Producto>) => {
      const { data } = await apiClient.post<Producto>('/productos/', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: productoKeys.all })
    },
  })
}

export function useActualizarProducto() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, ...payload }: Partial<Producto> & { id: number }) => {
      const { data } = await apiClient.put<Producto>(`/productos/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: productoKeys.all })
    },
  })
}

export function useEliminarProducto() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/productos/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: productoKeys.all })
    },
  })
}
