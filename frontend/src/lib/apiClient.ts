/**
 * Axios HTTP client with httpOnly cookie auth.
 *
 * The access_token and refresh_token are stored as httpOnly cookies
 * by the backend. The browser sends them automatically with every
 * request (withCredentials: true). The frontend never touches them.
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,  // Send cookies automatically
})

// ── Response interceptor (auto-refresh on 401) ─────────────────

interface TokenRefreshResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

let isRefreshing = false
let pendingQueue: Array<{
  resolve: (token: string) => void
  reject: (err: unknown) => void
}> = []

function processQueue(error: unknown, token: string | null = null): void {
  pendingQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token!)
    }
  })
  pendingQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    // Only attempt refresh on 401 and if we haven't retried yet
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error)
    }

    // If already refreshing, queue this request
    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        pendingQueue.push({ resolve, reject })
      }).then(() => {
        return apiClient(originalRequest)
      })
    }

    originalRequest._retry = true
    isRefreshing = true

    try {
      // The refresh_token cookie is sent automatically
      const { data } = await axios.post<TokenRefreshResponse>(
        `${API_URL}/auth/refresh`,
        {},
        { withCredentials: true },
      )

      processQueue(null, data.access_token)
      return apiClient(originalRequest)
    } catch (refreshError) {
      processQueue(refreshError, null)
      // Don't redirect here — the calling code (authStore.hydrate etc.)
      // handles 401s gracefully. Redirecting would cause a loop on /login.
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  },
)

export default apiClient
