import React, { useEffect, useState } from 'react';

interface PriceCardProps {
  /** Stock symbol to display */
  symbol: string;
  /** WebSocket endpoint providing price updates */
  wsUrl: string;
}

/**
 * Displays real-time price updates for a single stock symbol.
 * The component connects to a WebSocket feed and listens for
 * messages containing a `price` field.
 */
const PriceCard: React.FC<PriceCardProps> = ({ symbol, wsUrl }) => {
  const [price, setPrice] = useState<number | null>(null);

  useEffect(() => {
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      ws.send(JSON.stringify({ type: 'subscribe', symbol }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (typeof data.price === 'number') {
          setPrice(data.price);
        }
      } catch {
        // Ignore invalid messages
      }
    };

    return () => {
      ws.close();
    };
  }, [symbol, wsUrl]);

  return (
    <div className="price-card">
      <h3>{symbol}</h3>
      <p>{price !== null ? price.toFixed(2) : '—'}</p>
    </div>
  );
};

export default PriceCard;

