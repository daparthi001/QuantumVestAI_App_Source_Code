import { useQuery } from '@tanstack/react-query'
import { apiFetch } from '../client'

interface LatestData {
  trendingStocks: any
  trendingTopics: any
  twitterTrending: any
}

export function useLatestData() {
  return useQuery<LatestData>({
    queryKey: ['latest-data'],
    queryFn: async () => {
      const [trendingStocks, trendingTopics, twitterTrending] = await Promise.all([
        apiFetch('/v1/stocks/trending'),
        apiFetch('/v1/sentiment/trending/topics'),
        apiFetch('/social/twitter/trending'),
      ])
      return { trendingStocks, trendingTopics, twitterTrending }
    },
  })
}
