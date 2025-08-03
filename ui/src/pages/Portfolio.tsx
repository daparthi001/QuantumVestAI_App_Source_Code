import { useEffect, useState } from 'react'
import Watchlist from '@/components/Watchlist'
import TradePanel from '@/components/TradePanel'

interface Holding {
  symbol: string
  quantity: number
  value: number
}

/**
 * Portfolio dashboard displaying live performance of holdings along with
 * watchlist and trade panel components.
 */
export default function Portfolio() {
  const [holdings, setHoldings] = useState<Holding[]>([
    { symbol: 'AAPL', quantity: 10, value: 0 },
    { symbol: 'MSFT', quantity: 5, value: 0 },
  ])

  // WebSocket updates for live portfolio values
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/portfolio')
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data) as { symbol: string; value: number }
      setHoldings((prev) =>
        prev.map((h) =>
          h.symbol === data.symbol ? { ...h, value: data.value } : h
        )
      )
    }
    return () => ws.close()
  }, [])

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-2xl font-bold">Portfolio Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-2">
        {holdings.map((h) => (
          <div key={h.symbol} className="border p-4 rounded">
            <div className="font-semibold">{h.symbol}</div>
            <div>Qty: {h.quantity}</div>
            <div>Value: {h.value.toFixed(2)}</div>
          </div>
        ))}
      </div>
      <Watchlist />
      <TradePanel />
    </div>
  )
}

