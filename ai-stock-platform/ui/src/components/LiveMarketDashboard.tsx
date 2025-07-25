import React, { useEffect, useState } from 'react';

interface MarketData {
  portfolio?: any;
  market?: any;
  watchlist?: any;
  news?: any;
  aiInsights?: any;
  performance?: any;
}

const LiveMarketDashboard: React.FC = () => {
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [autoUpdate, setAutoUpdate] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMarketData = async () => {
    try {
      const response = await fetch('/api/market');
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();
      setMarketData(data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch market data:', err);
      setError('Unable to load market data. Please try again later.');
    }
  };

  useEffect(() => {
    fetchMarketData();
    if (!autoUpdate) return;
    const intervalId = setInterval(fetchMarketData, 15000);
    return () => clearInterval(intervalId);
  }, [autoUpdate]);

  return (
    <div className="dashboard">
      <div className="controls">
        <label>
          <input
            type="checkbox"
            checked={autoUpdate}
            onChange={() => setAutoUpdate(!autoUpdate)}
          />
          Auto Refresh
        </label>
        <button onClick={fetchMarketData}>Manual Refresh</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="widgets">
        <div className="widget">
          <h3>Portfolio Overview</h3>
          <pre>{JSON.stringify(marketData?.portfolio, null, 2)}</pre>
        </div>
        <div className="widget">
          <h3>Market Overview</h3>
          <pre>{JSON.stringify(marketData?.market, null, 2)}</pre>
        </div>
        <div className="widget">
          <h3>Watchlist</h3>
          <pre>{JSON.stringify(marketData?.watchlist, null, 2)}</pre>
        </div>
        <div className="widget">
          <h3>News</h3>
          <pre>{JSON.stringify(marketData?.news, null, 2)}</pre>
        </div>
        <div className="widget">
          <h3>AI Insights</h3>
          <pre>{JSON.stringify(marketData?.aiInsights, null, 2)}</pre>
        </div>
        <div className="widget">
          <h3>Performance</h3>
          <pre>{JSON.stringify(marketData?.performance, null, 2)}</pre>
        </div>
      </div>
    </div>
  );
};

export default LiveMarketDashboard;
