import { usePortfolioStore } from '@/store/portfolioStore'

export function usePortfolio() {
  const items = usePortfolioStore((s) => s.items)
  const addStock = usePortfolioStore((s) => s.addStock)
  return { items, addStock }
}
