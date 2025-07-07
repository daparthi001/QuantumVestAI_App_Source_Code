/**
 * Twitter Sentiment Component  
 * Created: 2025-01-08
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface TwitterSentimentProps {
  ticker: string;
}

const TwitterSentiment: React.FC<TwitterSentimentProps> = ({ ticker }) => {
  const [sentiment, setSentiment] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSentiment = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await axios.get(`/api/social/twitter/sentiment/${ticker}`);
        setSentiment(response.data);
      } catch (err: any) {
        // Check if this is a configuration error (HTTP 503)
        if (err.response && err.response.status === 503) {
          setError('Twitter integration not configured. Please set up Twitter API credentials.');
        } else {
          setError('Failed to load Twitter sentiment data');
        }
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (ticker) {
      fetchSentiment();
    }
  }, [ticker]);

  if (loading) return <div>Loading sentiment data...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!sentiment) return <div>No sentiment data available</div>;

  return (
    <div className="twitter-sentiment">
      <h3>Twitter Sentiment for {ticker}</h3>
      {/* Add sentiment visualization here */}
      <div>
        <p>Sentiment Score: {sentiment.score || 'N/A'}</p>
        <p>Volume: {sentiment.volume || 'N/A'}</p>
      </div>
    </div>
  );
};

export default TwitterSentiment;