import React from 'react'
import StockTicker from '@/components/Dashboard/StockTicker'
import PortfolioSummary from '@/components/Dashboard/PortfolioSummary'
import MarketNews from '@/components/Dashboard/MarketNews'
import SentimentChart from '@/components/Dashboard/SentimentChart'

export default function Dashboard() {
  return (
    <div className="space-y-4 p-4">
      <StockTicker />
      <PortfolioSummary />
      <MarketNews />
      <SentimentChart />
    </div>
  )
}
