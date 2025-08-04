export function connectMarketData(token: string): WebSocket {
  return new WebSocket(`wss://dev.quantumvestai.com/ws/market-data?token=${token}`);
}

