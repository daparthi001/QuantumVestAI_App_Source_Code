import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { apiFetch } from '@/api/client'

interface User {
  username: string
  [key: string]: any
}

interface AuthState {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refresh: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      async login(username, password) {
        const { data } = await apiFetch<{ data: { access_token: string } }>(
          '/auth/login',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
          },
        )
        set({ token: data?.access_token ?? null })
        await get().refresh()
      },
      async logout() {
        try {
          await apiFetch('/auth/logout', { method: 'POST' })
        } finally {
          set({ user: null, token: null })
        }
      },
      async refresh() {
        try {
          const user = await apiFetch<User>('/auth/me')
          set({ user })
        } catch {
          set({ user: null, token: null })
        }
      },
    }),
    {
      name: 'auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ user: state.user, token: state.token }),
    },
  ),
)

// Synchronize auth state across browser tabs
if (typeof window !== 'undefined') {
  window.addEventListener('storage', (e) => {
    if (e.key === 'auth' && e.newValue) {
      const parsed = JSON.parse(e.newValue)
      if (parsed?.state) {
        useAuthStore.setState(parsed.state)
      }
    }
  })
}
