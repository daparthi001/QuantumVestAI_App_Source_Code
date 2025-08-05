import { useAuthStore } from '@/store/useAuthStore'
import { Button } from '@/components/ui/button'

export default function Navbar() {
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)

  return (
    <nav className="flex items-center justify-between p-4 border-b mb-4 bg-gray-50">
      {user ? (
        <div className="flex items-center gap-4">
          <span>Welcome, {user.username}</span>
          <Button variant="outline" onClick={logout}>
            Logout
          </Button>
        </div>
      ) : (
        <div className="flex gap-4">
          <a className="text-blue-600 hover:underline" href="#login">
            Login
          </a>
          <a className="text-blue-600 hover:underline" href="#register">
            Register
          </a>
        </div>
      )}
    </nav>
  )
}
