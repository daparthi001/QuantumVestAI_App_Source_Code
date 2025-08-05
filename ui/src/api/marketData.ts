import { useAuthStore } from '@/store/useAuthStore'

const CHANNEL_NAME = 'market-data'

/**
 * Open a WebSocket connection for market data and broadcast messages across tabs.
 */
export function connectMarketData(token?: string): WebSocket {
  const t = token ?? useAuthStore.getState().token ?? ''
  const ws = new WebSocket(`wss://dev.quantumvestai.com/market-data?token=${t}`)
  const channel = new BroadcastChannel(CHANNEL_NAME)
  ws.onmessage = (event) => channel.postMessage(event.data)
  return ws
}

/**
 * Listen for market data updates broadcast by any tab.
 */
export function subscribeMarketData(handler: (data: string) => void): () => void {
  const channel = new BroadcastChannel(CHANNEL_NAME)
  channel.onmessage = (event) => handler(event.data as string)
  return () => channel.close()
}

