import { Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useCartStore, cartTotalItems } from '@/stores/cartStore'

export default function Navbar() {
  const { user, logout } = useAuthStore()
  const cartItems = useCartStore((s) => s.items)
  const totalItems = cartTotalItems(cartItems)

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-6">
          <Link to="/" className="text-xl font-bold text-gray-900">
            FoodStore
          </Link>
          <Link to="/productos" className="text-sm font-medium text-gray-600 hover:text-gray-900">
            Productos
          </Link>
          {user?.roles?.includes('ADMIN') && (
            <Link to="/admin" className="text-sm font-medium text-gray-600 hover:text-gray-900">
              Admin
            </Link>
          )}
        </div>

        <div className="flex items-center gap-3">
          <Link to="/perfil" className="text-sm font-medium text-gray-600 hover:text-gray-900">
            Mi Perfil
          </Link>
          <Link to="/pedidos" className="text-sm font-medium text-gray-600 hover:text-gray-900">
            Mis Pedidos
          </Link>

          {/* Cart link */}
          <Link to="/carrito" className="relative text-gray-600 hover:text-gray-900">
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z" />
            </svg>
            {totalItems > 0 && (
              <span className="absolute -right-2 -top-2 flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-[11px] font-bold text-white">
                {totalItems > 99 ? '99+' : totalItems}
              </span>
            )}
          </Link>

          <span className="text-sm text-gray-600">
            {user?.nombre} {user?.apellido}
          </span>
          <button
            onClick={logout}
            className="rounded-lg bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-200"
          >
            Cerrar sesión
          </button>
        </div>
      </div>
    </nav>
  )
}
