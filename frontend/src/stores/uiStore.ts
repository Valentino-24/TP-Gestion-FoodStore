import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// ── Types ──────────────────────────────────────────────────────

export type Theme = 'light' | 'dark'

export interface Toast {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
  duration?: number
}

interface UiState {
  theme: Theme
  sidebarOpen: boolean
  toasts: Toast[]
  toggleTheme: () => void
  setTheme: (theme: Theme) => void
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  addToast: (toast: Omit<Toast, 'id'>) => void
  dismissToast: (id: string) => void
}

// ── Helpers ────────────────────────────────────────────────────

let toastCounter = 0

function generateToastId(): string {
  toastCounter += 1
  return `toast-${toastCounter}-${Date.now()}`
}

function applyTheme(theme: Theme) {
  if (typeof document === 'undefined') return
  document.documentElement.classList.toggle('dark', theme === 'dark')
}

// ── Store ───────────────────────────────────────────────────────

export const useUiStore = create<UiState>()(
  persist(
    (set, get) => ({
      theme: 'light',
      sidebarOpen: false,
      toasts: [],

      toggleTheme: () => {
        const next = get().theme === 'light' ? 'dark' : 'light'
        applyTheme(next)
        set({ theme: next })
      },

      setTheme: (theme) => {
        applyTheme(theme)
        set({ theme })
      },

      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

      setSidebarOpen: (open) => set({ sidebarOpen: open }),

      addToast: (toast) => {
        const id = generateToastId()
        const newToast: Toast = { ...toast, id }
        set((s) => ({ toasts: [...s.toasts, newToast] }))

        // Auto-dismiss after duration (default 5000ms)
        const duration = toast.duration ?? 5000
        if (duration > 0) {
          setTimeout(() => {
            get().dismissToast(id)
          }, duration)
        }
      },

      dismissToast: (id) =>
        set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
    }),
    {
      name: 'foodstore-ui',
      partialize: (state) => ({ theme: state.theme }),
      onRehydrateStorage: () => (state) => {
        if (state?.theme) {
          applyTheme(state.theme)
        }
      },
    },
  ),
)
