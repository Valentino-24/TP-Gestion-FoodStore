import { useUiStore } from '@/stores/uiStore'
import type { Toast } from '@/stores/uiStore'

const TOAST_STYLES: Record<Toast['type'], { bg: string; icon: string; border: string }> = {
  success: { bg: 'bg-green-50', icon: '✅', border: 'border-green-200' },
  error: { bg: 'bg-red-50', icon: '❌', border: 'border-red-200' },
  info: { bg: 'bg-blue-50', icon: 'ℹ️', border: 'border-blue-200' },
  warning: { bg: 'bg-yellow-50', icon: '⚠️', border: 'border-yellow-200' },
}

export default function ToastContainer() {
  const toasts = useUiStore((s) => s.toasts)
  const dismissToast = useUiStore((s) => s.dismissToast)

  if (toasts.length === 0) return null

  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-[9999] flex flex-col gap-2">
      {toasts.map((toast) => {
        const style = TOAST_STYLES[toast.type]
        return (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-start gap-3 rounded-xl border ${style.border} ${style.bg} w-80 p-4 shadow-lg transition-all`}
          >
            <span className="mt-0.5 text-lg">{style.icon}</span>
            <p className="flex-1 text-sm text-gray-800">{toast.message}</p>
            <button
              onClick={() => dismissToast(toast.id)}
              className="text-gray-400 hover:text-gray-600"
              aria-label="Dismiss"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )
      })}
    </div>
  )
}
