import { Suspense, lazy } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { usePing } from '@/api/hooks/usePing'
import LatestData from '@/components/LatestData'
import Watchlist from '@/components/Watchlist'
import TradePanel from '@/components/TradePanel'

const Button = lazy(() => import('@/components/ui/button'))

export default function Home() {
  const count = useAppStore((s) => s.count)
  const increment = useAppStore((s) => s.increment)
  const { data } = usePing()

  return (
    <div className="container mx-auto p-4 space-y-4">
      <h1 className="text-2xl font-bold">QuantumVest AI UI</h1>
      <p>{data?.message ?? 'Loading...'}</p>
      <div>Count: {count}</div>
      <Suspense fallback={<div>Loading button...</div>}>
        <Button onClick={increment}>Increment</Button>
      </Suspense>
      <LatestData />
      <div className="grid gap-4 md:grid-cols-2">
        <Watchlist />
        <TradePanel />
      </div>
    </div>
  )
}
