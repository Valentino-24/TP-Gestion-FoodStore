import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

const ALLOWED_ROLES = ['COCINA', 'PEDIDOS', 'ADMIN']

export default function CocinaRoute() {
  const { isAuthenticated, user, isLoading } = useAuthStore()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  const hasAccess = user?.roles?.some((role) => ALLOWED_ROLES.includes(role))
  if (!hasAccess) {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
