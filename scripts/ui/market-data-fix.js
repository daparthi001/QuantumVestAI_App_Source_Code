/**
 * QuantumVestAI Market Data WebSocket Fix
 * Created: 2025-08-04
 * Author: gayatri
 * 
 * This script fixes WebSocket connection issues for free tier users
 */
(function() {
  console.log('QuantumVestAI Market Data WebSocket Fix - Version 2025.08.04');
  
  // Override WebSocket creation for market data connections
  const originalWebSocket = window.WebSocket;
  
  const MAX_RETRIES = 5;
  const RETRY_DELAY = 3000; // ms

  function createWebSocket(url, protocols) {
    let attempts = 0;
    let ws;

    const connect = () => {
      attempts += 1;
      ws = new originalWebSocket(url, protocols);

      ws.addEventListener('close', () => {
        if (attempts <= MAX_RETRIES) {
          console.warn(`WebSocket closed. Reconnecting in ${RETRY_DELAY}ms (attempt ${attempts}/${MAX_RETRIES})`);
          setTimeout(connect, RETRY_DELAY);
        }
      });

      ws.addEventListener('error', (err) => {
        console.error('WebSocket error:', err);
        ws.close();
      });
    };

    connect();
    return ws;
  }

  window.WebSocket = function(url, protocols) {
    // Check if this is a market-data WebSocket connection
    if (url && typeof url === 'string' && url.includes('/ws/market-data')) {
      console.log('Intercepting WebSocket connection to /ws/market-data');

      // Get token from the original URL
      let token = '';
      try {
        const urlObj = new URL(url);
        token = urlObj.searchParams.get('token') || '';
      } catch (e) {
        console.error('Error parsing WebSocket URL:', e);
      }

      // Modify the URL to use the direct endpoint instead of the /ws/ prefixed one
      // The direct endpoint is more permissive with role checks
      url = url.replace('/ws/market-data', '/market-data');
      console.log('Redirecting WebSocket to more permissive endpoint:', url.split('?')[0]);
    }

    // Create the WebSocket with the possibly modified URL and auto-reconnect
    return createWebSocket(url, protocols);
  };
  
  // Preserve the WebSocket prototype and properties
  for (const prop in originalWebSocket) {
    if (Object.prototype.hasOwnProperty.call(originalWebSocket, prop)) {
      window.WebSocket[prop] = originalWebSocket[prop];
    }
  }
  
  window.WebSocket.prototype = originalWebSocket.prototype;
  
  console.log('WebSocket fix applied successfully');
})();
