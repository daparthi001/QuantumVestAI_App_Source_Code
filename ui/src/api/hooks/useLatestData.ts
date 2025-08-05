import { useQuery } from '@tanstack/react-query'
import { apiFetch } from '../client'
import { fetchTrendingStocks, TrendingStock } from '../trending'

interface LatestData {
  trendingStocks: TrendingStock[]
  trendingTopics: any
  twitterTrending: any
}

export function useLatestData() {
  return useQuery<LatestData>({
    queryKey: ['latest-data'],
    queryFn: async () => {
      const [trendingStocks, trendingTopics, twitterTrending] = await Promise.all([
        fetchTrendingStocks(),
        apiFetch('/v1/sentiment/trending/topics'),
        apiFetch('/social/twitter/trending'),
      ])
      return { trendingStocks, trendingTopics, twitterTrending }
    },
  })
}
