export function connectMarketData(token: string): WebSocket {
  // Connect directly to the market-data endpoint which allows free-tier access.
  return new WebSocket(`wss://dev.quantumvestai.com/market-data?token=${token}`);
}

