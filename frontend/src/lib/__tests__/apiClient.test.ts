/**
 * Tests for apiClient (axios instance with httpOnly cookie auth).
 *
 * With httpOnly cookies, the client simply sends cookies automatically
 * via withCredentials. No token management in JS.
 */

import { describe, it, expect } from 'vitest'

describe('apiClient config', () => {
  it('has withCredentials set to true', async () => {
    const mod = await import('../apiClient')
    const apiClient = mod.default
    expect(apiClient.defaults.withCredentials).toBe(true)
  })

  it('uses the correct base URL', async () => {
    const mod = await import('../apiClient')
    const apiClient = mod.default
    expect(apiClient.defaults.baseURL).toMatch(/\/api\/v1$/)
  })

  it('has JSON content type', async () => {
    const mod = await import('../apiClient')
    const apiClient = mod.default
    expect(apiClient.defaults.headers['Content-Type']).toBe('application/json')
  })

  it('does not export legacy token helpers', async () => {
    const mod = await import('../apiClient')
    expect(mod).not.toHaveProperty('storeTokens')
    expect(mod).not.toHaveProperty('clearTokens')
    expect(mod).not.toHaveProperty('getStoredAccessToken')
    expect(mod).not.toHaveProperty('getStoredRefreshToken')
  })
})
