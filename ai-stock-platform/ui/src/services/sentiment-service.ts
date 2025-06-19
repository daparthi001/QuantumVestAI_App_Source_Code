/**
 * Sentiment Analysis Service
 * Created: 2025-06-19 03:09:13
 * Author: daparthi001
 */
import { api } from './api';

export interface SentimentData {
  symbol: string;
  date: string;
  sentiment_score: number;
  sentiment_label: 'positive' | 'negative' | 'neutral';
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
    source: string;
    sentiment: number;
    url?: string;
    engagement: number;
  }>;
}

export interface TrendingStock {
  symbol: string;
  company_name: string;
  sentiment_score: number;
  mention_count: number;
  change_24h: number;
  trending_score: number;
}

export const sentimentService = {
  /**
   * Get sentiment analysis for a specific stock
   */
  async getStockSentiment(symbol: string): Promise<SentimentData> {
    try {
      const response = await api.get(`/sentiment/${symbol}`);
      return response.data.data;
    } catch (error) {
      console.error(`Error fetching sentiment for ${symbol}:`, error);
      throw error;
    }
  },

  /**
   * Get historical sentiment data for a stock
   */
  async getHistoricalSentiment(
    symbol: string, 
    startDate: string, 
    endDate: string
  ): Promise<SentimentData[]> {
    try {
      const response = await api.get(`/sentiment/${symbol}/historical`, {
        params: { start_date: startDate, end_date: endDate }
      });
      return response.data.data;
    } catch (error) {
      console.error(`Error fetching historical sentiment for ${symbol}:`, error);
      throw error;
    }
  },

  /**
   * Get trending stocks based on social media activity
   */
  async getTrendingStocks(limit: number = 10): Promise<TrendingStock[]> {
    try {
      const response = await api.get('/sentiment/trending', {
        params: { limit }
      });
      return response.data.data;
    } catch (error) {
      console.error('Error fetching trending stocks:', error);
      throw error;
    }
  },

  /**
   * Get real-time sentiment updates
   * This uses server-sent events for real-time updates
   */
  subscribeToRealtimeSentiment(symbol: string, callback: (data: SentimentData) => void): () => void {
    const eventSource = new EventSource(`${api.defaults.baseURL}/sentiment/${symbol}/realtime`);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      callback(data);
    };
    
    eventSource.onerror = (error) => {
      console.error('Error in sentiment EventSource:', error);
      eventSource.close();
    };
    
    // Return unsubscribe function
    return () => {
      eventSource.close();
    };
  }
};