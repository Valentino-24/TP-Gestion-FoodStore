/**
 * Hook that manages the SSE connection to the KDS backend.
 *
 * - On mount: opens EventSource to GET /api/v1/cocina/eventos
 * - Handles PEDIDO_CONFIRMADO, PEDIDO_EN_PREPARACION, PEDIDO_EN_CAMINO, PEDIDO_CANCELADO
 * - Falls back to polling (30s) if SSE disconnects
 * - Reconnects automatically (native EventSource behavior)
 * - Plays a beep sound when a new pedido arrives (US-COCINA-05)
 *
 * Relies on httpOnly cookies for auth (same as REST API).
 */

import { useEffect, useRef, useCallback } from 'react'
import { useCocinaStore } from './cocinaStore'
import type { KitchenSSEEvent } from './types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
const POLL_INTERVAL = 30_000
const SOUND_ENABLED_KEY = 'kds_sound_enabled'

/**
 * Play a short beep using Web Audio API.
 * Requires a prior user interaction (autoplay policy).
 */
function playBeep() {
  try {
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)()
    const oscillator = ctx.createOscillator()
    const gain = ctx.createGain()

    oscillator.connect(gain)
    gain.connect(ctx.destination)

    oscillator.type = 'sine'
    oscillator.frequency.setValueAtTime(880, ctx.currentTime) // A5
    gain.gain.setValueAtTime(0.3, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3)

    oscillator.start(ctx.currentTime)
    oscillator.stop(ctx.currentTime + 0.3)
  } catch {
    // Audio not available — silently ignore
  }
}

function isSoundEnabled(): boolean {
  return localStorage.getItem(SOUND_ENABLED_KEY) !== 'false'
}

export function useCocinaSSE() {
  const {
    fetchPedidos,
    addPedido,
    movePedido,
    removePedido,
    setSSEConnected,
    pedidos,
  } = useCocinaStore()

  const eventSourceRef = useRef<EventSource | null>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const startPolling = useCallback(() => {
    if (pollingRef.current) return
    pollingRef.current = setInterval(() => {
      fetchPedidos()
    }, POLL_INTERVAL)
  }, [fetchPedidos])

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [])

  useEffect(() => {
    // Initial load
    fetchPedidos()

    const url = `${API_URL}/cocina/eventos`
    const es = new EventSource(url, { withCredentials: true })
    eventSourceRef.current = es

    es.addEventListener('connected', () => {
      setSSEConnected(true)
      stopPolling()
    })

    es.addEventListener('PEDIDO_CONFIRMADO', (event: MessageEvent) => {
      try {
        const data: KitchenSSEEvent = JSON.parse(event.data)
        // Play sound alert if enabled
        if (isSoundEnabled()) {
          playBeep()
        }
        fetchPedidos()
      } catch {
        // Ignore parse errors
      }
    })

    es.addEventListener('PEDIDO_EN_PREPARACION', (event: MessageEvent) => {
      try {
        const data: KitchenSSEEvent = JSON.parse(event.data)
        movePedido(data.pedido_id, 'EN_PREPARACION')
      } catch {
        // Ignore parse errors
      }
    })

    es.addEventListener('PEDIDO_EN_CAMINO', (event: MessageEvent) => {
      try {
        const data: KitchenSSEEvent = JSON.parse(event.data)
        removePedido(data.pedido_id)
      } catch {
        // Ignore parse errors
      }
    })

    es.addEventListener('PEDIDO_CANCELADO', (event: MessageEvent) => {
      try {
        const data: KitchenSSEEvent = JSON.parse(event.data)
        removePedido(data.pedido_id)
      } catch {
        // Ignore parse errors
      }
    })

    es.onerror = () => {
      setSSEConnected(false)
      startPolling()
    }

    es.onopen = () => {
      setSSEConnected(true)
      stopPolling()
    }

    return () => {
      es.close()
      eventSourceRef.current = null
      stopPolling()
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps
}
