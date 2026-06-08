/**
 * TimerUrgencia — displays elapsed time since kitchen entry.
 *
 * Recalculates every 15s and applies urgency styling:
 * - < 10 min: normal
 * - 10–20 min: warning (orange)
 * - > 20 min: urgent (red)
 */

import { useState, useEffect } from 'react'

interface TimerUrgenciaProps {
  kitchenEntryAt: string | null
}

function getElapsedMinutes(kitchenEntryAt: string | null): number {
  if (!kitchenEntryAt) return 0
  const entry = new Date(kitchenEntryAt).getTime()
  const now = Date.now()
  return Math.floor((now - entry) / 60_000)
}

export function TimerUrgencia({ kitchenEntryAt }: TimerUrgenciaProps) {
  const [elapsed, setElapsed] = useState(() => getElapsedMinutes(kitchenEntryAt))

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(getElapsedMinutes(kitchenEntryAt))
    }, 15_000)
    return () => clearInterval(interval)
  }, [kitchenEntryAt])

  const minutes = elapsed
  const isWarning = minutes >= 10 && minutes < 20
  const isUrgent = minutes >= 20

  let colorClass = 'text-gray-600'
  let bgClass = 'bg-gray-50 border-gray-200'
  if (isWarning) {
    colorClass = 'text-orange-600'
    bgClass = 'bg-orange-50 border-orange-300'
  }
  if (isUrgent) {
    colorClass = 'text-red-600'
    bgClass = 'bg-red-50 border-red-300'
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium border ${colorClass} ${bgClass}`}
    >
      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      {minutes < 60 ? `${minutes} min` : `${Math.floor(minutes / 60)}h ${minutes % 60}m`}
    </span>
  )
}
