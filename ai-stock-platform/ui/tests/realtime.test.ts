import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
const RealtimeService = require('../static/js/realtime.js')

class MockWebSocket {
  static instances: MockWebSocket[] = []
  url: string
  readyState: number
  onopen: ((ev?: any) => void) | null = null
  onmessage: ((ev: { data: string }) => void) | null = null
  onclose: ((ev: { code: number }) => void) | null = null
  onerror: ((ev: any) => void) | null = null
  sent: string[] = []
  constructor(url: string) {
    this.url = url
    this.readyState = MockWebSocket.OPEN
    MockWebSocket.instances.push(this)
  }
  send(data: string) {
    this.sent.push(data)
  }
  close() {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) this.onclose({ code: 1006 })
  }
}
MockWebSocket.OPEN = 1
MockWebSocket.CLOSED = 3

describe('RealtimeService', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    // @ts-ignore
    global.WebSocket = MockWebSocket
    MockWebSocket.instances = []
  })

  afterEach(() => {
    vi.useRealTimers()
    // @ts-ignore
    delete global.WebSocket
  })

  it('reconnects when connection drops', () => {
    const service = new RealtimeService('token', { maxReconnectAttempts: 1, reconnectDelay: 100 })
    service.connect()
    const first = MockWebSocket.instances[0]
    first.onopen && first.onopen()
    first.onclose && first.onclose({ code: 1006 })
    expect(MockWebSocket.instances.length).toBe(1)
    vi.advanceTimersByTime(100)
    expect(MockWebSocket.instances.length).toBe(2)
  })

  it('ignores malformed JSON messages', () => {
    const service = new RealtimeService('token')
    const cb = vi.fn()
    service.subscribe('price_update', cb)
    service.connect()
    const socket = MockWebSocket.instances[0]
    socket.onopen && socket.onopen()
    socket.onmessage && socket.onmessage({ data: '{ bad json' })
    expect(cb).not.toHaveBeenCalled()
  })
})
