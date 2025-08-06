import React from 'react'

export default function Card({ children }: { children: React.ReactNode }) {
  return <div className="rounded border p-4 shadow bg-white">{children}</div>
}
