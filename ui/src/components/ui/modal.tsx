import * as React from 'react'

import { cn } from '@/lib/utils'
import { Button } from './button'

interface ModalProps {
  open: boolean
  onClose: () => void
  title?: string
  children?: React.ReactNode
  className?: string
}

export function Modal({ open, onClose, title, children, className }: ModalProps) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div
        className={cn(
          'w-full max-w-md rounded-md bg-white p-4 shadow-lg dark:bg-gray-800',
          className
        )}
      >
        {title && <h2 className="mb-2 text-lg font-semibold">{title}</h2>}
        <div>{children}</div>
        <div className="mt-4 text-right">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  )
}
