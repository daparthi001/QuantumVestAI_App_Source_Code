import { useEffect, useRef } from 'react'

export function useWebSocket(url: string) {
  const socketRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const socket = new WebSocket(url)
    socketRef.current = socket
    return () => {
      socket.close()
    }
  }, [url])

  return socketRef.current
}
