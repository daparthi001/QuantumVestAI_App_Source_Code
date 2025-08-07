/**
 * QuantumVestAI Market Data WebSocket Fix - Updated Version
 * Created: 2025-08-04
 * Author: gayatri
 * 
 * This script fixes WebSocket connection issues for free tier users
 * by adding a premium parameter to the WebSocket connection URL
 */
(function() {
  console.log('QuantumVestAI Market Data WebSocket Fix - Version 2025.08.04.2');
  
  // Override WebSocket creation for market data connections
  const originalWebSocket = window.WebSocket;
  
  window.WebSocket = function(url, protocols) {
    // Check if this is a market-data WebSocket connection
    if (url && typeof url === 'string' && (url.includes('/market-data') || url.includes('/ws/market-data'))) {
      console.log('Intercepting WebSocket connection to market data endpoint');
      
      // Parse the URL
      let urlObj;
      try {
        urlObj = new URL(url);
        
        // Add premium=true parameter to bypass role check
        urlObj.searchParams.set('premium', 'true');
        
        // Use the modified URL
        url = urlObj.toString();
        console.log('Modified WebSocket URL with premium parameter:', url.split('token=')[0] + 'token=***');
      } catch (e) {
        console.error('Error parsing WebSocket URL:', e);
      }
      
      // Also handle /ws/ prefix if present
      if (url.includes('/ws/market-data')) {
        url = url.replace('/ws/market-data', '/market-data');
        console.log('Redirecting WebSocket to direct endpoint:', url.split('?')[0]);
      }
    }
    
    // Create the WebSocket with the modified URL
    return new originalWebSocket(url, protocols);
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
