import React from 'react'
import { usePortfolio } from '@/hooks/usePortfolio'
import Card from '@/components/Shared/Card'

export default function Portfolio() {
  const { items } = usePortfolio()
  return (
    <div className="space-y-2 p-4">
      {items.map((s) => (
        <Card key={s}>{s}</Card>
      ))}
    </div>
  )
}
