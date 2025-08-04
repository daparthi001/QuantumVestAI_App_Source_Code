import { create } from 'zustand'
import { apiFetch } from '@/api/client'

interface User {
  username: string
  [key: string]: any
}

interface AuthState {
  user: User | null
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refresh: () => Promise<void>
}

export const useAuthStore = create<AuthState>()((set, get) => ({
  user: null,
  async login(username, password) {
    await apiFetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    await get().refresh()
  },
  async logout() {
    try {
      await apiFetch('/auth/logout', { method: 'POST' })
    } finally {
      set({ user: null })
    }
  },
  async refresh() {
    try {
      const user = await apiFetch<User>('/auth/me')
      set({ user })
    } catch {
      set({ user: null })
    }
  },
}))
