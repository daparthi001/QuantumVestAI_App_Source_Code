import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Modal } from '@/components/ui/modal'
import { Card } from '@/components/ui/card'

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
  const [toRemove, setToRemove] = useState<string | null>(null)

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
    <Card title="Watchlist" className="space-y-2">
      <div className="flex space-x-2">
        <Input
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          placeholder="Symbol"
          className="w-32"
        />
        <Button onClick={addSymbol}>Add</Button>
      </div>
      <ul className="space-y-1 max-h-64 overflow-y-auto">
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
            <Button
              variant="outline"
              className="text-red-600 border-red-600 hover:bg-red-50"
              onClick={() => setToRemove(item.symbol)}
            >
              Remove
            </Button>
          </li>
        ))}
      </ul>
      <Modal
        open={toRemove !== null}
        onClose={() => setToRemove(null)}
        title="Remove symbol?"
      >
        <p className="mb-4">Remove {toRemove} from watchlist?</p>
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => setToRemove(null)}>
            Cancel
          </Button>
          <Button
            onClick={() => {
              if (toRemove) removeSymbol(toRemove)
              setToRemove(null)
            }}
          >
            Remove
          </Button>
        </div>
      </Modal>
    </Card>
  )
}

