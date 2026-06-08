import { Outlet } from 'react-router-dom'
import Navbar from '@/widgets/Navbar'
import ErrorBoundary from '@/shared/ui/ErrorBoundary'
import ToastContainer from '@/shared/ui/ToastContainer'

export default function LayoutAuth() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </main>
        <ToastContainer />
      </div>
    </ErrorBoundary>
  )
}
