import { Button } from '@/components/ui/button'
import { useAppStore } from '@/store/useAppStore'
import { usePing } from '@/api/hooks/usePing'

function App() {
  const count = useAppStore((s) => s.count)
  const increment = useAppStore((s) => s.increment)
  const { data } = usePing()

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">QuantumVest AI UI</h1>
      <p>{data?.message ?? 'Loading...'}</p>
      <div>Count: {count}</div>
      <Button onClick={increment}>Increment</Button>
    </div>
  )
}

export default App
