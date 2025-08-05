import { useState } from 'react'
import { useAuthStore } from '@/store/useAuthStore'
import { Button } from '@/components/ui/button'

export default function LoginForm() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const login = useAuthStore((s) => s.login)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await login(username, password)
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3 p-4 max-w-sm">
      <input
        className="border p-2 rounded-md"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        className="border p-2 rounded-md"
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <Button type="submit" className="mt-2">
        Login
      </Button>
    </form>
  )
}
