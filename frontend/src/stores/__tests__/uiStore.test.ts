/**
 * Tests for uiStore (Zustand with persist middleware).
 *
 * Note: uiStore uses `zustand/middleware/persist`, so we must be careful
 * about side-effects from rehydration and localStorage.
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useUiStore } from '../uiStore'

describe('uiStore', () => {
  beforeEach(() => {
    // Reset localStorage to clear persisted state
    localStorage.clear()

    // Reset the store to defaults by calling setTheme('light')
    // This also clears the toasts and resets sidebar
    useUiStore.setState({
      theme: 'light',
      sidebarOpen: false,
      toasts: [],
    })
  })

  describe('theme', () => {
    it('starts with light theme', () => {
      expect(useUiStore.getState().theme).toBe('light')
    })

    it('toggleTheme switches light → dark', () => {
      useUiStore.getState().toggleTheme()
      expect(useUiStore.getState().theme).toBe('dark')
    })

    it('toggleTheme switches dark → light', () => {
      useUiStore.getState().setTheme('dark')
      useUiStore.getState().toggleTheme()
      expect(useUiStore.getState().theme).toBe('light')
    })

    it('setTheme sets the theme', () => {
      useUiStore.getState().setTheme('dark')
      expect(useUiStore.getState().theme).toBe('dark')
    })
  })

  describe('sidebar', () => {
    it('starts closed', () => {
      expect(useUiStore.getState().sidebarOpen).toBe(false)
    })

    it('toggleSidebar opens when closed', () => {
      useUiStore.getState().toggleSidebar()
      expect(useUiStore.getState().sidebarOpen).toBe(true)
    })

    it('toggleSidebar closes when open', () => {
      useUiStore.getState().toggleSidebar()
      useUiStore.getState().toggleSidebar()
      expect(useUiStore.getState().sidebarOpen).toBe(false)
    })

    it('setSidebarOpen sets the value', () => {
      useUiStore.getState().setSidebarOpen(true)
      expect(useUiStore.getState().sidebarOpen).toBe(true)
    })
  })

  describe('toasts', () => {
    it('starts with empty toasts', () => {
      expect(useUiStore.getState().toasts).toHaveLength(0)
    })

    it('addToast adds a toast with generated id', () => {
      useUiStore.getState().addToast({ type: 'success', message: 'Done!' })

      const toasts = useUiStore.getState().toasts
      expect(toasts).toHaveLength(1)
      expect(toasts[0].message).toBe('Done!')
      expect(toasts[0].type).toBe('success')
      expect(toasts[0].id).toMatch(/^toast-\d+-\d+$/)
    })

    it('addToast defaults duration to undefined (store uses 5000ms internally)', () => {
      useUiStore.getState().addToast({ type: 'info', message: 'Info' })

      const toast = useUiStore.getState().toasts[0]
      // Duration is not stored on the toast when using default — the store
      // uses `?? 5000` internally for the setTimeout call
      expect(toast.duration).toBeUndefined()
    })

    it('addToast respects custom duration', () => {
      useUiStore.getState().addToast({
        type: 'warning',
        message: 'Warning',
        duration: 2000,
      })

      const toast = useUiStore.getState().toasts[0]
      expect(toast.duration).toBe(2000)
    })

    it('addToast supports warning type', () => {
      useUiStore.getState().addToast({
        type: 'warning',
        message: 'Careful!',
      })
      expect(useUiStore.getState().toasts[0].type).toBe('warning')
    })

    it('adds multiple toasts', () => {
      useUiStore.getState().addToast({ type: 'success', message: 'A' })
      useUiStore.getState().addToast({ type: 'error', message: 'B' })
      useUiStore.getState().addToast({ type: 'info', message: 'C' })

      expect(useUiStore.getState().toasts).toHaveLength(3)
    })

    it('dismissToast removes by id', () => {
      useUiStore.getState().addToast({ type: 'success', message: 'First' })
      useUiStore.getState().addToast({ type: 'error', message: 'Second' })

      const firstId = useUiStore.getState().toasts[0].id
      useUiStore.getState().dismissToast(firstId)

      const toasts = useUiStore.getState().toasts
      expect(toasts).toHaveLength(1)
      expect(toasts[0].message).toBe('Second')
    })
  })
})
