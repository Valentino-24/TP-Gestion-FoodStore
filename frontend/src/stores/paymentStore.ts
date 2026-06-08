import { create } from 'zustand'

// ── Types ──────────────────────────────────────────────────────

export type PaymentStatus = 'idle' | 'processing' | 'success' | 'error'

interface PaymentState {
  status: PaymentStatus
  mpPaymentId: string | null
  errorDetail: string | null
  setPaymentStatus: (status: PaymentStatus) => void
  setMpPaymentId: (id: string | null) => void
  setErrorDetail: (detail: string | null) => void
  resetPayment: () => void
}

// ── Store ───────────────────────────────────────────────────────

export const usePaymentStore = create<PaymentState>((set) => ({
  status: 'idle',
  mpPaymentId: null,
  errorDetail: null,

  setPaymentStatus: (status) => set({ status }),

  setMpPaymentId: (mpPaymentId) => set({ mpPaymentId }),

  setErrorDetail: (errorDetail) => set({ errorDetail }),

  resetPayment: () => set({
    status: 'idle',
    mpPaymentId: null,
    errorDetail: null,
  }),
}))
