/**
 * Twitter Sentiment Component  
 * Created: 2025-01-08
 * Updated: 2025-01-09 (Enhanced with better error handling and real-time updates)
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface TwitterSentimentProps {
  ticker: string;
}

interface SentimentData {
  symbol: string;
  date: string;
  sentiment_score: number;
  sentiment_label: string;
  volume: number;
  trending_score: number;
  sources: {
    twitter: number;
    reddit: number;
    news: number;
    other: number;
  };
  top_mentions: Array<{
    text: string;
    sentiment: number;
    source: string;
    url: string;
    engagement: number;
  }>;
  daily_sentiment: Array<{
    date: string;
    sentiment_score: number;
    volume: number;
  }>;
  note?: string;
}

const TwitterSentiment: React.FC<TwitterSentimentProps> = ({ ticker }) => {
  const [sentiment, setSentiment] = useState<SentimentData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSentiment = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Use the new social API endpoint structure
        const response = await axios.get(`/api/social/twitter/sentiment/${ticker}`);
        
        if (response.data.status === 'success') {
          setSentiment(response.data.data);
        } else {
          // Handle API error response
          setError(response.data.error || 'Failed to load sentiment data');
        }
      } catch (err: any) {
        // Check if this is a configuration error (HTTP 503)
        if (err.response && err.response.status === 503) {
          setError('Twitter integration not configured. Please set up Twitter API credentials.');
        } else if (err.response && err.response.status === 429) {
          setError('Twitter API rate limit exceeded. Please try again later.');
        } else {
          setError('Failed to load Twitter sentiment data');
        }
        console.error('Twitter sentiment error:', err);
      } finally {
        setLoading(false);
      }
    };

    if (ticker) {
      fetchSentiment();
    }
  }, [ticker]);

  const getSentimentColor = (score: number) => {
    if (score > 0.1) return '#28a745'; // Green for positive
    if (score < -0.1) return '#dc3545'; // Red for negative
    return '#6c757d'; // Gray for neutral
  };

  const getSentimentIcon = (label: string) => {
    switch (label) {
      case 'positive': return '📈';
      case 'negative': return '📉';
      default: return '➖';
    }
  };

  if (loading) return (
    <div className="twitter-sentiment-loading">
      <div className="spinner-border spinner-border-sm me-2" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
      Loading sentiment data...
    </div>
  );

  if (error) return (
    <div className="twitter-sentiment-error alert alert-warning">
      <i className="fas fa-exclamation-triangle me-2"></i>
      {error}
    </div>
  );

  if (!sentiment) return (
    <div className="twitter-sentiment-empty alert alert-info">
      <i className="fas fa-info-circle me-2"></i>
      No sentiment data available for {ticker}
    </div>
  );

  return (
    <div className="twitter-sentiment">
      <div className="card">
        <div className="card-header d-flex justify-content-between align-items-center">
          <h5 className="mb-0">
            <i className="fab fa-twitter me-2" style={{color: '#1da1f2'}}></i>
            Twitter Sentiment for {sentiment.symbol}
          </h5>
          {sentiment.note && (
            <small className="text-muted">{sentiment.note}</small>
          )}
        </div>
        
        <div className="card-body">
          {/* Main Sentiment Score */}
          <div className="row mb-3">
            <div className="col-md-6">
              <div className="sentiment-score text-center">
                <div className="display-4" style={{color: getSentimentColor(sentiment.sentiment_score)}}>
                  {getSentimentIcon(sentiment.sentiment_label)} {sentiment.sentiment_score.toFixed(2)}
                </div>
                <div className="text-muted">
                  <strong>{sentiment.sentiment_label.toUpperCase()}</strong> sentiment
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="sentiment-stats">
                <div className="row text-center">
                  <div className="col-6">
                    <div className="stat-value">{sentiment.volume}</div>
                    <div className="stat-label text-muted">Tweets</div>
                  </div>
                  <div className="col-6">
                    <div className="stat-value">{sentiment.trending_score.toFixed(1)}</div>
                    <div className="stat-label text-muted">Trending Score</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Sources Breakdown */}
          <div className="mb-3">
            <h6 className="text-muted mb-2">Sources</h6>
            <div className="row">
              <div className="col-3 text-center">
                <div className="text-primary fw-bold">{sentiment.sources.twitter}</div>
                <small className="text-muted">Twitter</small>
              </div>
              <div className="col-3 text-center">
                <div className="text-secondary fw-bold">{sentiment.sources.reddit}</div>
                <small className="text-muted">Reddit</small>
              </div>
              <div className="col-3 text-center">
                <div className="text-info fw-bold">{sentiment.sources.news}</div>
                <small className="text-muted">News</small>
              </div>
              <div className="col-3 text-center">
                <div className="text-dark fw-bold">{sentiment.sources.other}</div>
                <small className="text-muted">Other</small>
              </div>
            </div>
          </div>

          {/* Top Mentions */}
          {sentiment.top_mentions && sentiment.top_mentions.length > 0 && (
            <div className="mb-3">
              <h6 className="text-muted mb-2">Top Mentions</h6>
              <div className="list-group list-group-flush">
                {sentiment.top_mentions.slice(0, 3).map((mention, index) => (
                  <div key={index} className="list-group-item px-0 py-2">
                    <div className="d-flex justify-content-between align-items-start">
                      <div className="flex-grow-1">
                        <p className="mb-1 small">{mention.text}</p>
                        <small className="text-muted">
                          Engagement: {mention.engagement} | 
                          Sentiment: <span style={{color: getSentimentColor(mention.sentiment)}}>
                            {mention.sentiment.toFixed(2)}
                          </span>
                        </small>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Last Updated */}
          <div className="text-muted small text-center">
            Last updated: {sentiment.date} | {sentiment.volume} tweets analyzed
          </div>
        </div>
      </div>
    </div>
  );
};

export default TwitterSentiment;