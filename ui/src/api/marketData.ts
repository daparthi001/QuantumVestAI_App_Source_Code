export function connectMarketData(token: string): WebSocket {
  // Try connecting to the direct endpoint first (without /ws/ prefix)
  // as it's more permissive with token validation
  try {
    return new WebSocket(`wss://dev.quantumvestai.com/market-data?token=${token}`);
  } catch (err) {
    console.warn("Failed to connect to direct market-data endpoint, falling back to /ws/ path");
    return new WebSocket(`wss://dev.quantumvestai.com/ws/market-data?token=${token}`);
  }
}

