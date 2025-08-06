import React, { useEffect, useState } from 'react'
import { fetchJSON } from '@/services/api'

interface SettingsResponse {
  [key: string]: unknown
}

export default function Settings() {
  const [settings, setSettings] = useState<SettingsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const data = await fetchJSON<SettingsResponse>('/api/settings')
        setSettings(data)
      } catch (err) {
        console.error('Failed to load settings', err)
        setError('Failed to load settings')
      } finally {
        setLoading(false)
      }
    }

    loadSettings()
  }, [])

  if (loading) {
    return (
      <div className="flex justify-center p-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-blue-500"></div>
      </div>
    )
  }

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>
  }

  if (!settings || Object.keys(settings).length === 0) {
    return <div className="p-4">No settings found</div>
  }

  return (
    <div className="p-4">
      <pre className="text-sm">{JSON.stringify(settings, null, 2)}</pre>
    </div>
  )
}
