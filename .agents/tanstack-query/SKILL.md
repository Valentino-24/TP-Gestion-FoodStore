---
name: tanstack-query
description: |
  Server state management with TanStack Query (React Query). Includes query keys, caching, mutations, optimistic updates, and integration with Zustand.

  Use when fetching API data, managing server state, implementing optimistic UI updates, or handling pagination/infinite queries.
---

# TanStack Query (React Query)

**Dependencies**: @tanstack/react-query@5.x

---

## Quick Start

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
})

// In App root
<QueryClientProvider client={queryClient}>
  <App />
</QueryClientProvider>
```

---

## Basic Query

```typescript
import { useQuery } from '@tanstack/react-query'

interface Product {
  id: number
  name: string
  price: number
}

function ProductList() {
  const { data, isLoading, error } = useQuery<Product[]>({
    queryKey: ['products'],
    queryFn: () => fetch('/api/products').then(r => r.json()),
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <ul>
      {data?.map(p => <li key={p.id}>{p.name}</li>)}
    </ul>
  )
}
```

---

## Query Key Organization

```typescript
// Products
queryKey: ['products']
queryKey: ['products', categoryId]           // By category
queryKey: ['products', categoryId, page]    // Paginated

// Single item
queryKey: ['product', productId]

// User-specific
queryKey: ['user', 'orders', userId]
queryKey: ['user', 'cart', userId]
```

---

## Mutations

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'

function CreateOrderButton() {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (newOrder: Order) =>
      fetch('/api/orders', {
        method: 'POST',
        body: JSON.stringify(newOrder),
      }).then(r => r.json()),

    // Invalidar queries relacionadas
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      queryClient.invalidateQueries({ queryKey: ['cart', userId] })
    },
  })

  return (
    <button
      onClick={() => mutation.mutate({ items: [...] })}
      disabled={mutation.isPending}
    >
      {mutation.isPending ? 'Creating...' : 'Create Order'}
    </button>
  )
}
```

---

## Optimistic Updates

```typescript
const mutation = useMutation({
  mutationFn: updateProduct,
  onMutate: async (newProduct) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['product', newProduct.id] })

    // Snapshot previous value
    const previous = queryClient.getQueryData(['product', newProduct.id])

    // Optimistically update
    queryClient.setQueryData(['product', newProduct.id], newProduct)

    return { previous }
  },
  onError: (err, newProduct, context) => {
    // Rollback on error
    queryClient.setQueryData(['product', newProduct.id], context.previous)
  },
  onSettled: (data, error, variables) => {
    // Refetch to ensure sync
    queryClient.invalidateQueries({ queryKey: ['product', variables.id] })
  },
})
```

---

## Infinite/ Pagination

```typescript
import { useInfiniteQuery } from '@tanstack/react-query'

function ProductList() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['products', categoryId],
    queryFn: ({ pageParam = 0 }) =>
      fetch(`/api/products?page=${pageParam}`).then(r => r.json()),
    getNextPageParam: (lastPage) => lastPage.nextPage ?? undefined,
    initialPageParam: 0,
  })

  return (
    <div>
      {data?.pages.map(page =>
        page.items.map(product => <ProductCard key={product.id} {...product} />)
      )}
      <button
        onClick={() => fetchNextPage()}
        disabled={!hasNextPage || isFetchingNextPage}
      >
        Load More
      </button>
    </div>
  )
}
```

---

## React Query + Zustand Pattern

```typescript
// Zustand for client state (cart, auth)
const useCartStore = create<CartStore>()(...)

// React Query for server state (products, orders)
const { data } = useQuery({ queryKey: ['products'], queryFn: fetchProducts })

// They complement each other, don't replace
```

---

## Critical Rules

✅ Use query keys: `['entity', id, filters]`
✅ Invalidate on mutations with `onSuccess`
✅ Use optimistic updates for better UX
✅ Don't use Query for client-only state
✅ Set `staleTime` to avoid over-fetching

---

## Resources

- **TanStack Query**: https://tanstack.com/query
- **Docs**: https://tanstack.com/query/latest/docs/framework/react/overview