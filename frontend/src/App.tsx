import { useEffect } from 'react'
import { RouterProvider } from 'react-router-dom'
import router from '@/router'
import { useAuthStore } from '@/stores/authStore'

export default function App() {
  const hydrate = useAuthStore((state) => state.hydrate)

  useEffect(() => {
    hydrate()
  }, [hydrate])

  return <RouterProvider router={router} />
}
