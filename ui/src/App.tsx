import { Suspense, lazy } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { usePing } from '@/api/hooks/usePing'

// Lazy load non-critical UI components
const Button = lazy(() => import('@/components/ui/button'))

function App() {
  const count = useAppStore((s) => s.count)
  const increment = useAppStore((s) => s.increment)
  const { data } = usePing()

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">QuantumVest AI UI</h1>
      <p>{data?.message ?? 'Loading...'}</p>
      <div>Count: {count}</div>
      <Suspense fallback={<div>Loading button...</div>}>
        <Button onClick={increment}>Increment</Button>
      </Suspense>
    </div>
  )
}

export default App
