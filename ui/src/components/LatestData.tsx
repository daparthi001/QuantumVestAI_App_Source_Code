import { useLatestData } from '@/api/hooks/useLatestData'

export default function LatestData() {
  const { data, isLoading, error } = useLatestData()

  if (isLoading) {
    return <div>Loading latest data...</div>
  }

  if (error || !data) {
    return <div>Failed to load latest data</div>
  }

  const trendingStocksCount = data.trendingStocks?.stocks?.length ?? 0
  const trendingTopicsCount = data.trendingTopics?.topics?.length ?? 0
  const twitterTrendingCount = data.twitterTrending?.trending_tickers?.length ?? 0

  return (
    <div className="space-y-2">
      <h2 className="text-xl font-semibold">Latest Data</h2>
      <div>Trending Stocks: {trendingStocksCount}</div>
      <div>Trending Topics: {trendingTopicsCount}</div>
      <div>Twitter Trending: {twitterTrendingCount}</div>
    </div>
  )
}
