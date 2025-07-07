/**
 * Stock Service
 * Created: 2025-01-08
 * Author: daparthi001
 */
import apiClient from './api';

export interface StockData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap?: number;
  peRatio?: number;
  dividend?: number;
  high52Week?: number;
  low52Week?: number;
}

export interface TechnicalIndicators {
  date: string;
  sma20: number;
  sma50: number;
  sma200: number;
  rsi: number;
  macd: number;
  macdSignal: number;
  macdHistogram: number;
  bollingerUpper: number;
  bollingerMiddle: number;
  bollingerLower: number;
}

export interface SentimentData {
  overallScore: number;
  sources: {
    news: number;
    social: number;
    analyst: number;
  };
  historical: Array<{
    date: string;
    score: number;
    volume: number;
  }>;
  topMentions: Array<{
    source: string;
    title: string;
    sentiment: number;
    url: string;
    timestamp: string;
  }>;
}

class StockService {
  async getStockData(symbol: string): Promise<StockData> {
    const response = await apiClient.get(`/api/v1/stocks/${symbol}`);
    return response.data;
  }

  async getStockQuote(symbol: string): Promise<StockData> {
    const response = await apiClient.get(`/api/v1/stocks/${symbol}/quote`);
    return response.data;
  }

  async getTechnicalIndicators(symbol: string): Promise<{ data: TechnicalIndicators[] }> {
    const response = await apiClient.get(`/api/v1/stocks/${symbol}/technical`);
    return response.data;
  }

  async getSentimentAnalysis(symbol: string): Promise<{ data: SentimentData }> {
    const response = await apiClient.get(`/api/v1/stocks/${symbol}/sentiment`);
    return response.data;
  }

  async searchStocks(query: string): Promise<StockData[]> {
    const response = await apiClient.get(`/api/v1/stocks/search?q=${query}`);
    return response.data;
  }

  async getHistoricalData(symbol: string, period: string = '1y'): Promise<any> {
    const response = await apiClient.get(`/api/v1/stocks/${symbol}/history?period=${period}`);
    return response.data;
  }

  async getMarketData(): Promise<any> {
    const response = await apiClient.get('/api/v1/market/overview');
    return response.data;
  }
}

const stockService = new StockService();
export default stockService;