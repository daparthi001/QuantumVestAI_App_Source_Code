import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'

// Simple light/dark mode toggle that persists the choice in localStorage
export function ThemeToggle() {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    if (typeof window === 'undefined') {
      return 'light'
    }
    return window.localStorage.getItem('theme') === 'dark' ? 'dark' : 'light'
  })

  useEffect(() => {
    const root = window.document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    window.localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))
  }

  return (
    <Button onClick={toggleTheme} variant="outline">
      {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
    </Button>
  )
}

export default ThemeToggle
