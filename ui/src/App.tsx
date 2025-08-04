import { useEffect } from 'react'
import Navbar from '@/components/Navbar'
import LoginForm from '@/components/LoginForm'
import Home from '@/components/Home'
import { useAuthStore } from '@/store/useAuthStore'

function App() {
  const user = useAuthStore((s) => s.user)
  const refresh = useAuthStore((s) => s.refresh)

  useEffect(() => {
    refresh()
  }, [refresh])

  return (
    <div>
      <Navbar />
      {user ? <Home /> : <LoginForm />}
    </div>
  )
}

export default App
