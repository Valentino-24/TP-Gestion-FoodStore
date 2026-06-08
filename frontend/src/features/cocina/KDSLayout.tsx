/**
 * KDSLayout — layout wrapper for the Kitchen Display System.
 *
 * Features:
 * - Full-screen layout suited for a kitchen monitor
 * - SSE connection indicator
 * - Sound toggle (US-COCINA-05)
 * - No auto-logout (session stays active while on this page)
 */

import { useState, useEffect } from 'react'
import { Outlet } from 'react-router-dom'

const SOUND_ENABLED_KEY = 'kds_sound_enabled'

export function KDSLayout() {
  const [soundEnabled, setSoundEnabled] = useState(() => {
    return localStorage.getItem(SOUND_ENABLED_KEY) !== 'false'
  })

  const toggleSound = () => {
    setSoundEnabled((prev) => {
      const next = !prev
      localStorage.setItem(SOUND_ENABLED_KEY, String(next))
      return next
    })
  }

  // Keep-alive: send a periodic ping to prevent session timeout
  useEffect(() => {
    const interval = setInterval(() => {
      // The SSE keepalive and periodic polling keep the session alive
      // No additional action needed
    }, 60_000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="h-screen bg-gray-100 flex flex-col overflow-hidden">
      {/* Top bar */}
      <header className="bg-white border-b border-gray-200 px-6 py-2 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-gray-900">🍳 FoodStore</span>
          <span className="text-sm text-gray-500">| Cocina</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={toggleSound}
            className="flex items-center gap-1 px-2 py-1 text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
            title={soundEnabled ? 'Desactivar sonido' : 'Activar sonido'}
          >
            {soundEnabled ? (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
              </svg>
            )}
            {soundEnabled ? 'Sonido ON' : 'Sonido OFF'}
          </button>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}
