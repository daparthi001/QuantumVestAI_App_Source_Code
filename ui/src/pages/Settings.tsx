import { useState } from 'react'
import ThemeToggle from '@/components/ThemeToggle'
import { Button } from '@/components/ui/button'

function Settings() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">Profile Settings</h1>
      <div className="space-y-2">
        <label className="block">
          <span className="text-sm">Name</span>
          <input
            className="w-full border p-2 rounded-md"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm">Email</span>
          <input
            className="w-full border p-2 rounded-md"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
      </div>
      <div>
        <ThemeToggle />
      </div>
      <Button type="button">Save</Button>
    </div>
  )
}

export default Settings
