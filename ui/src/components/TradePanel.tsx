import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

interface Trade {
  symbol: string
  quantity: number
  side: 'buy' | 'sell'
}

/**
 * Simple panel that simulates trade actions. Trades are stored locally
 * and displayed in a list.
 */
export default function TradePanel() {
  const [symbol, setSymbol] = useState('')
  const [quantity, setQuantity] = useState(0)
  const [log, setLog] = useState<Trade[]>([])

  const handleTrade = (side: 'buy' | 'sell') => {
    const s = symbol.trim().toUpperCase()
    if (!s || quantity <= 0) return
    setLog((prev) => [...prev, { symbol: s, quantity, side }])
    setSymbol('')
    setQuantity(0)
  }

  return (
    <div className="space-y-2">
      <h2 className="text-xl font-semibold">Trade</h2>
      <div className="flex space-x-2">
        <Input
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          placeholder="Symbol"
          className="w-32"
        />
        <Input
          type="number"
          value={quantity}
          onChange={(e) => setQuantity(parseInt(e.target.value) || 0)}
          placeholder="Qty"
          className="w-24"
        />
        <Button onClick={() => handleTrade('buy')}>Buy</Button>
        <Button onClick={() => handleTrade('sell')}>Sell</Button>
      </div>
      <ul className="space-y-1">
        {log.map((t, idx) => (
          <li key={idx} className="text-sm">
            {t.side.toUpperCase()} {t.quantity} {t.symbol}
          </li>
        ))}
      </ul>
    </div>
  )
}

