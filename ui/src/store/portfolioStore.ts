import { create } from 'zustand'

interface PortfolioState {
  items: string[]
  addStock: (symbol: string) => void
}

export const usePortfolioStore = create<PortfolioState>((set) => ({
  items: [],
  addStock: (symbol) => set((s) => ({ items: [...s.items, symbol] })),
}))
