/**
 * Tests for apiClient (axios instance with interceptors).
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  storeTokens,
  clearTokens,
  getStoredAccessToken,
  getStoredRefreshToken,
} from '../apiClient'

describe('Token helpers', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('storeTokens saves access and refresh tokens', () => {
    storeTokens('access-123', 'refresh-456')
    expect(localStorage.getItem('access_token')).toBe('access-123')
    expect(localStorage.getItem('refresh_token')).toBe('refresh-456')
  })

  it('getStoredAccessToken returns null when no token', () => {
    expect(getStoredAccessToken()).toBeNull()
  })

  it('getStoredAccessToken returns stored token', () => {
    localStorage.setItem('access_token', 'my-token')
    expect(getStoredAccessToken()).toBe('my-token')
  })

  it('getStoredRefreshToken returns stored refresh token', () => {
    localStorage.setItem('refresh_token', 'my-refresh')
    expect(getStoredRefreshToken()).toBe('my-refresh')
  })

  it('clearTokens removes both tokens', () => {
    localStorage.setItem('access_token', 'acc')
    localStorage.setItem('refresh_token', 'ref')
    clearTokens()
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })
})

describe('API client interceptors', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('request interceptor adds Authorization header when token exists', async () => {
    // We need to import the client dynamically after setting up localStorage
    localStorage.setItem('access_token', 'test-bearer-token')

    // Dynamic import to get the client with fresh localStorage
    const mod = await import('../apiClient')
    const apiClient = mod.default

    // Intercept a request and check headers
    const intercepted = await apiClient.interceptors.request.handlers[0].fulfilled({
      headers: { Authorization: '' },
      method: 'get',
      url: '/test',
    } as any)

    expect(intercepted.headers.Authorization).toBe('Bearer test-bearer-token')
  })

  it('request interceptor skips Authorization when no token', async () => {
    const mod = await import('../apiClient')
    const apiClient = mod.default

    const config = {
      headers: {},
      method: 'get',
      url: '/test',
    } as any

    const intercepted = await apiClient.interceptors.request.handlers[0].fulfilled(config)
    // Should not have Authorization header since no token
    expect(intercepted.headers.Authorization || '').toBe('')
  })
})
