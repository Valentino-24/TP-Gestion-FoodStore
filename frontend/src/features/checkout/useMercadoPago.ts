import { useEffect, useRef, useState } from 'react'

type MPStatus = 'loading' | 'ready' | 'error'

interface CardData {
  cardNumber: string
  cardExpirationMonth: string
  cardExpirationYear: string
  securityCode: string
  cardholderName: string
}

/**
 * Hook that loads MercadoPago SDK v2 and exposes
 * createCardToken() for tokenization.
 *
 * In this version of the SDK, createCardToken is an async
 * function that returns a Promise (not callback-based).
 */
export function useMercadoPago() {
  const [status, setStatus] = useState<MPStatus>('loading')
  const initializedRef = useRef(false)

  useEffect(() => {
    if (initializedRef.current) return
    initializedRef.current = true

    const publicKey = import.meta.env.VITE_MP_PUBLIC_KEY as string

    if (!publicKey) {
      console.error('[MP] VITE_MP_PUBLIC_KEY missing')
      setStatus('error')
      return
    }

    const check = () => {
      if (window.MercadoPago) {
        try {
          window.mpInstance = new window.MercadoPago(publicKey)
          const cct = window.mpInstance.createCardToken
          console.log('[MP] SDK initialized. createCardToken is async, args:', cct?.length)
          setStatus('ready')
        } catch (err) {
          console.error('[MP] Constructor error:', err)
          setStatus('error')
        }
      } else {
        setTimeout(check, 200)
      }
    }

    setTimeout(check, 500)
  }, [])

  /**
   * Creates a card token via MercadoPago SDK.
   * Uses the async/Promise-based API (not callback).
   */
  const createCardToken = async (cardData: CardData): Promise<string> => {
    const mp = window.mpInstance
    if (!mp) throw new Error('MercadoPago no inicializado')

    if (typeof mp.createCardToken !== 'function') {
      throw new Error('createCardToken no disponible')
    }

    const payload = {
      cardNumber: cardData.cardNumber.replace(/\s/g, ''),
      cardExpirationMonth: cardData.cardExpirationMonth.padStart(2, '0'),
      cardExpirationYear: cardData.cardExpirationYear,
      securityCode: cardData.securityCode,
      cardholderName: cardData.cardholderName,
    }

    // This is an async function that returns { id: string }
    const response = await mp.createCardToken(payload)
    console.log('[MP] createCardToken result:', response)

    // The response might be { id: "token_..." } or the token string itself
    const token = typeof response === 'string' ? response : (response as Record<string, unknown>)?.id as string
    if (!token) {
      throw new Error('No se generó el token de tarjeta')
    }

    return token
  }

  return { createCardToken, status }
}

// ── Types ──────────────────────────────────────────────────────

interface MPInstance {
  createCardToken: (data: Record<string, string>) => Promise<unknown>
}

declare global {
  interface Window {
    MercadoPago?: new (key: string) => MPInstance
    mpInstance?: MPInstance
  }
}
