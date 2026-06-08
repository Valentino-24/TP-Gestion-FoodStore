import { createBrowserRouter } from 'react-router-dom'

import LayoutPublic from '@/components/LayoutPublic'
import LayoutAuth from '@/components/LayoutAuth'
import LayoutAdmin from '@/components/LayoutAdmin'
import ProtectedRoute from '@/components/ProtectedRoute'
import AdminRoute from '@/components/AdminRoute'
import CocinaRoute from '@/components/CocinaRoute'

import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import HomePage from '@/pages/HomePage'
import ProductListPage from '@/pages/ProductListPage'
import ProductDetailPage from '@/pages/ProductDetailPage'
import CartPage from '@/pages/CartPage'
import CheckoutPage from '@/pages/CheckoutPage'
import PaymentPage from '@/pages/PaymentPage'
import OrdersPage from '@/pages/OrdersPage'
import OrderDetailPage from '@/pages/OrderDetailPage'
import AddressesPage from '@/pages/AddressesPage'
import ProfilePage from '@/pages/ProfilePage'
import AdminDashboard from '@/pages/AdminDashboard'
import ProductosAdminPage from '@/pages/admin/ProductosAdminPage'
import CategoriasAdminPage from '@/pages/admin/CategoriasAdminPage'
import ClientesAdminPage from '@/pages/admin/ClientesAdminPage'
import PedidosAdminPage from '@/pages/admin/PedidosAdminPage'

import { KDSLayout } from '@/features/cocina/KDSLayout'
import { KDSPage } from '@/features/cocina/KDSPage'

const router = createBrowserRouter([
  {
    // Public routes (no auth required)
    element: <LayoutPublic />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/register', element: <RegisterPage /> },
    ],
  },
  {
    // Authenticated routes (token required)
    element: <ProtectedRoute />,
    children: [
      {
        element: <LayoutAuth />,
        children: [
          { path: '/', element: <HomePage /> },
          { path: '/productos', element: <ProductListPage /> },
          { path: '/productos/:id', element: <ProductDetailPage /> },
          { path: '/carrito', element: <CartPage /> },
          { path: '/checkout', element: <CheckoutPage /> },
          { path: '/pago/:pedidoId', element: <PaymentPage /> },
          { path: '/pedidos', element: <OrdersPage /> },
          { path: '/pedidos/:id', element: <OrderDetailPage /> },
          { path: '/perfil', element: <ProfilePage /> },
          { path: '/perfil/direcciones', element: <AddressesPage /> },
        ],
      },
    ],
  },
  {
    // Admin routes (ADMIN role required)
    element: <AdminRoute />,
    children: [
      {
        element: <LayoutAdmin />,
        children: [
          { path: '/admin', element: <AdminDashboard /> },
          { path: '/admin/productos', element: <ProductosAdminPage /> },
          { path: '/admin/categorias', element: <CategoriasAdminPage /> },
          { path: '/admin/clientes', element: <ClientesAdminPage /> },
          { path: '/admin/pedidos', element: <PedidosAdminPage /> },
        ],
      },
    ],
  },
  {
    // KDS routes (COCINA / PEDIDOS / ADMIN role required)
    element: <CocinaRoute />,
    children: [
      {
        element: <KDSLayout />,
        children: [
          { path: '/cocina', element: <KDSPage /> },
        ],
      },
    ],
  },
])

export default router
