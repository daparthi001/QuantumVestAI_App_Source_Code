import { useLatestData } from '@/api/hooks/useLatestData'
import { Card } from '@/components/ui/card'

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
    <Card title="Latest Data" className="space-y-4">
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
    </Card>
  )
}
