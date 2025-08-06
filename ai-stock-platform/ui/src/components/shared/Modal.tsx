import React from 'react'

interface ModalProps {
  open: boolean
  onClose(): void
  children: React.ReactNode
}

export default function Modal({ open, onClose, children }: ModalProps) {
  if (!open) return null
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50">
      <div className="bg-white p-4 rounded shadow">
        {children}
        <button className="mt-4" onClick={onClose}>Close</button>
      </div>
    </div>
  )
}
