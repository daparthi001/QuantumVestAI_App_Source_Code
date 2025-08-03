import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'

interface WatchItem {
  symbol: string
  price?: number
}

/**
 * Displays a list of stock symbols and keeps their price updated using a WebSocket.
 * Users can add or remove symbols from the list.
 */
export default function Watchlist() {
  const [symbol, setSymbol] = useState('')
  const [items, setItems] = useState<WatchItem[]>([])

  // Establish a websocket connection for live price updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/watchlist')
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data) as WatchItem
      setItems((prev) =>
        prev.map((item) =>
          item.symbol === data.symbol ? { ...item, price: data.price } : item
        )
      )
    }
    return () => ws.close()
  }, [])

  const addSymbol = () => {
    const s = symbol.trim().toUpperCase()
    if (!s) return
    setItems((prev) =>
      prev.some((i) => i.symbol === s) ? prev : [...prev, { symbol: s }]
    )
    setSymbol('')
  }

  const removeSymbol = (s: string) => {
    setItems((prev) => prev.filter((i) => i.symbol !== s))
  }

  return (
    <div className="space-y-2">
      <h2 className="text-xl font-semibold">Watchlist</h2>
      <div className="flex space-x-2">
        <input
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          placeholder="Symbol"
          className="border px-2 py-1 rounded"
        />
        <Button onClick={addSymbol}>Add</Button>
      </div>
      <ul className="space-y-1">
        {items.map((item) => (
          <li
            key={item.symbol}
            className="flex justify-between items-center border-b pb-1"
          >
            <span>
              {item.symbol}
              {item.price !== undefined && (
                <span className="ml-2 text-sm text-gray-500">
                  {item.price.toFixed(2)}
                </span>
              )}
            </span>
            <button
              onClick={() => removeSymbol(item.symbol)}
              className="text-red-500 text-sm"
            >
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

