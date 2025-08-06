import * as React from 'react'
import { cn } from '@/lib/utils'

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
}

export function Card({ title, className, children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'p-4 bg-white dark:bg-gray-800 rounded shadow-sm',
        className
      )}
      {...props}
    >
      {title && <h2 className="text-xl font-semibold">{title}</h2>}
      {children}
    </div>
  )
}
