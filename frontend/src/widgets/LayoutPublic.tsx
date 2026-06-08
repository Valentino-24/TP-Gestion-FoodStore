import { Outlet } from 'react-router-dom'
import ErrorBoundary from '@/shared/ui/ErrorBoundary'

export default function LayoutPublic() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <ErrorBoundary>
          <Outlet />
        </ErrorBoundary>
      </div>
    </ErrorBoundary>
  )
}
