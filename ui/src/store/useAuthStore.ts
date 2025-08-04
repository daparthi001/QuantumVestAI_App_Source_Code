import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { apiFetch } from '@/api/client'

interface User {
  username: string
  [key: string]: any
}

interface AuthState {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  refresh: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      async login(username, password) {
        const res = await apiFetch<{ token: string; user: User }>(
          '/auth/login',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
          }
        )
        set({ token: res.token, user: res.user })
      },
      logout() {
        set({ user: null, token: null })
      },
      async refresh() {
        const token = get().token
        if (!token) return
        try {
          const user = await apiFetch<User>('/auth/me', {
            headers: { Authorization: `Bearer ${token}` },
          })
          set({ user })
        } catch {
          set({ user: null, token: null })
        }
      },
    }),
    { name: 'auth' }
  )
)
