import { apiFetch } from './client'

export interface TrendingStock {
  symbol: string
  name: string
  price: number
  change: number
  change_percent: number
  volume: number
  last_updated: string
}

/**
 * Fetch the list of trending stocks from the API and return the stocks array.
 */
export async function fetchTrendingStocks(): Promise<TrendingStock[]> {
  const data = await apiFetch<{ stocks: TrendingStock[] }>('/v1/stocks/trending')
  return data.stocks
}
