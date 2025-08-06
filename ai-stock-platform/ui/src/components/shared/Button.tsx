import React, { ButtonHTMLAttributes } from 'react'

export default function Button({ className = '', ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button className={`px-3 py-1 rounded bg-blue-600 text-white ${className}`} {...props} />
}
