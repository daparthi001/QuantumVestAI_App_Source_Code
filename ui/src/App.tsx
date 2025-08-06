import React from 'react'
import Navbar from '@/components/Layout/Navbar'
import Sidebar from '@/components/Layout/Sidebar'
import Footer from '@/components/Layout/Footer'
import Dashboard from '@/pages/Dashboard'

export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1">
          <Dashboard />
        </main>
      </div>
      <Footer />
    </div>
  )
}
