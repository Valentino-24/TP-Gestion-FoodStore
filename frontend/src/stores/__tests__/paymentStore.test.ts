/**
 * Tests for paymentStore (Zustand, no persistence).
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { usePaymentStore } from '../paymentStore'

describe('paymentStore', () => {
  beforeEach(() => {
    usePaymentStore.getState().resetPayment()
  })

  describe('initial state', () => {
    it('starts idle with no payment data', () => {
      const state = usePaymentStore.getState()
      expect(state.status).toBe('idle')
      expect(state.mpPaymentId).toBeNull()
      expect(state.errorDetail).toBeNull()
    })
  })

  describe('setPaymentStatus', () => {
    it('updates status to processing', () => {
      usePaymentStore.getState().setPaymentStatus('processing')
      expect(usePaymentStore.getState().status).toBe('processing')
    })

    it('updates status to success', () => {
      usePaymentStore.getState().setPaymentStatus('success')
      expect(usePaymentStore.getState().status).toBe('success')
    })

    it('updates status to error', () => {
      usePaymentStore.getState().setPaymentStatus('error')
      expect(usePaymentStore.getState().status).toBe('error')
    })
  })

  describe('setMpPaymentId', () => {
    it('stores payment ID', () => {
      usePaymentStore.getState().setMpPaymentId('mp-123456')
      expect(usePaymentStore.getState().mpPaymentId).toBe('mp-123456')
    })

    it('clears payment ID with null', () => {
      usePaymentStore.getState().setMpPaymentId('mp-123456')
      usePaymentStore.getState().setMpPaymentId(null)
      expect(usePaymentStore.getState().mpPaymentId).toBeNull()
    })
  })

  describe('setErrorDetail', () => {
    it('stores error message', () => {
      usePaymentStore.getState().setErrorDetail('Payment rejected')
      expect(usePaymentStore.getState().errorDetail).toBe('Payment rejected')
    })
  })

  describe('resetPayment', () => {
    it('resets all fields to initial state', () => {
      // Set various states
      usePaymentStore.getState().setPaymentStatus('success')
      usePaymentStore.getState().setMpPaymentId('mp-789')
      usePaymentStore.getState().setErrorDetail('some error')

      // Reset
      usePaymentStore.getState().resetPayment()

      // Verify all reset
      const state = usePaymentStore.getState()
      expect(state.status).toBe('idle')
      expect(state.mpPaymentId).toBeNull()
      expect(state.errorDetail).toBeNull()
    })
  })

  describe('combined flow', () => {
    it('handles a complete payment flow: idle → processing → success', () => {
      expect(usePaymentStore.getState().status).toBe('idle')

      usePaymentStore.getState().setPaymentStatus('processing')
      expect(usePaymentStore.getState().status).toBe('processing')

      usePaymentStore.getState().setMpPaymentId('mp-final')
      usePaymentStore.getState().setPaymentStatus('success')
      expect(usePaymentStore.getState().status).toBe('success')
      expect(usePaymentStore.getState().mpPaymentId).toBe('mp-final')
    })

    it('handles a failed payment flow: idle → processing → error', () => {
      usePaymentStore.getState().setPaymentStatus('processing')
      usePaymentStore.getState().setErrorDetail('Insufficient funds')
      usePaymentStore.getState().setPaymentStatus('error')

      const state = usePaymentStore.getState()
      expect(state.status).toBe('error')
      expect(state.errorDetail).toBe('Insufficient funds')
    })
  })
})
