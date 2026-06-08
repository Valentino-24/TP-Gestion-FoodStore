import { Component, type ReactNode, type ErrorInfo } from 'react'
import { Link } from 'react-router-dom'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('[ErrorBoundary]', error, info.componentStack)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="flex min-h-[50vh] flex-col items-center justify-center px-4 text-center">
          <span className="mb-4 text-6xl">💥</span>
          <h1 className="text-2xl font-bold text-gray-900">Algo salió mal</h1>
          <p className="mt-2 max-w-md text-gray-500">
            Ocurrió un error inesperado. No te preocupes, ya lo registramos.
          </p>
          <div className="mt-6 flex gap-3">
            <button
              onClick={() => window.location.reload()}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Recargar página
            </button>
            <Link
              to="/"
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Volver al inicio
            </Link>
          </div>
          {(import.meta.env.DEV) && this.state.error && (
            <pre className="mt-6 max-w-xl overflow-auto rounded-lg bg-red-50 p-4 text-left text-xs text-red-700">
              {this.state.error.message}
              {this.state.error.stack}
            </pre>
          )}
        </div>
      )
    }

    return this.props.children
  }
}
