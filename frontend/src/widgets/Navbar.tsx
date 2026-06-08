import { Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useCartStore, cartTotalItems } from '@/stores/cartStore'
import { useUiStore } from '@/stores/uiStore'

export default function Navbar() {
  const { user, logout } = useAuthStore()
  const cartItems = useCartStore((s) => s.items)
  const totalItems = cartTotalItems(cartItems)
  const { theme, toggleTheme, toggleSidebar } = useUiStore()

  return (
    <nav className="border-b border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-6">
          {/* Mobile menu toggle */}
          <button
            onClick={toggleSidebar}
            className="rounded-lg p-2 text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 lg:hidden"
            aria-label="Toggle menu"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <Link to="/" className="text-xl font-bold text-gray-900 dark:text-white">
            FoodStore
          </Link>
          <Link to="/productos" className="hidden text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white sm:inline">
            Productos
          </Link>
          {user?.roles?.includes('ADMIN') && (
            <Link to="/admin" className="hidden text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white sm:inline">
              Admin
            </Link>
          )}
          {user?.roles?.some((r) => ['COCINA', 'PEDIDOS', 'ADMIN'].includes(r)) && (
            <Link to="/cocina" className="hidden text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white sm:inline">
              Cocina
            </Link>
          )}
        </div>

        <div className="flex items-center gap-3">
          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="rounded-lg p-2 text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            ) : (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            )}
          </button>
          <Link to="/perfil" className="text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
            Mi Perfil
          </Link>
          <Link to="/pedidos" className="text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
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
