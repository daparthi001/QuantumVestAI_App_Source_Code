import { useAuthStore } from '@/store/useAuthStore'

export default function Navbar() {
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)

  return (
    <nav className="flex gap-4 p-4 border-b mb-4">
      {user ? (
        <>
          <span>Welcome, {user.username}</span>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <>
          <a href="#login">Login</a>
          <a href="#register">Register</a>
        </>
      )}
    </nav>
  )
}
