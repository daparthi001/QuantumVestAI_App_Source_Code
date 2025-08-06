import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'

interface Trade {
  symbol: string
  quantity: number
  side: 'buy' | 'sell'
}

export default function TradePanel() {
  const [symbol, setSymbol] = useState('')
  const [quantity, setQuantity] = useState<number | ''>('')
  const [log, setLog] = useState<Trade[]>([])

  const handleTrade = (side: 'buy' | 'sell') => {
    const s = symbol.trim().toUpperCase()
    const qty = typeof quantity === 'string' ? parseInt(quantity) : quantity
    if (!s || !qty || !Number.isFinite(qty) || qty <= 0) return
    setLog((prev) => [...prev, { symbol: s, quantity: qty, side }])
    setSymbol('')
    setQuantity('')
  }

  return (
    <Card title="Trade" className="space-y-2">
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
          onChange={(e) => {
            const val = e.target.value
            if (val === '') {
              setQuantity('')
            } else {
              const parsed = parseInt(val)
              setQuantity(Number.isFinite(parsed) && parsed > 0 ? parsed : '')
            }
          }}
          placeholder="Qty"
          className="w-24"
          min={1}
        />
        <Button onClick={() => handleTrade('buy')}>Buy</Button>
        <Button onClick={() => handleTrade('sell')}>Sell</Button>
      </div>
      <ul className="space-y-1 max-h-64 overflow-y-auto">
        {log.map((t, idx) => (
          <li key={idx} className="text-sm">
            {t.side.toUpperCase()} {t.quantity} {t.symbol}
          </li>
        ))}
      </ul>
    </Card>
  )
}

