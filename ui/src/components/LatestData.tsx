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
    <div className="p-4 bg-white rounded shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Latest Data</h2>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
        <div className="p-2 border rounded">
          Trending Stocks: {trendingStocksCount}
        </div>
        <div className="p-2 border rounded">
          Trending Topics: {trendingTopicsCount}
        </div>
        <div className="p-2 border rounded">
          Twitter Trending: {twitterTrendingCount}
        </div>
      </div>
    </div>
  )
}
