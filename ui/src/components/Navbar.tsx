import { useAuthStore } from '@/store/useAuthStore'
import { Button } from '@/components/ui/button'
import ThemeToggle from '@/components/ThemeToggle'

export default function Navbar() {
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)

  return (
    <nav className="flex items-center justify-between p-4 border-b bg-gray-50 shadow-sm sticky top-0 z-50 w-full">
      {user ? (
        <div className="flex items-center gap-4">
          <span>Welcome, {user.username}</span>
          <Button variant="outline" onClick={logout}>
            Logout
          </Button>
        </div>
      ) : (
        <div className="flex gap-4">
          <a className="text-primary hover:underline" href="#login">
            Login
          </a>
          <a className="text-primary hover:underline" href="#register">
            Register
          </a>
        </div>
      )}
      <ThemeToggle />
    </nav>
  )
}
