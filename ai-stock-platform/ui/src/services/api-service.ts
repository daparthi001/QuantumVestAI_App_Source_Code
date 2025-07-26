/**
 * Advanced API Service for All Endpoints
 * Updated: 2025-06-19 18:06:43
 * Author: daparthi001
 */
import apiClient from './api';
import { API_ENDPOINTS } from '../config/constants';

// Define response types
interface StandardResponse<T> {
  status: string;
  message?: string;
  data: T;
}

// Stock interfaces
export interface Stock {
  symbol: string;
  name: string;
  price: number;
  change_percent: number;
  change?: number;
  market_cap?: string;
  pe_ratio?: number;
  dividend_yield?: number;
  '52_week_high'?: number;
  '52_week_low'?: number;
}

// Prediction interfaces
export interface Prediction {
  date: string;
  price: number;
  confidence: number;
}

export interface StockPrediction {
  symbol: string;
  current_price: number;
  prediction_date: string;
  predictions: Prediction[];
  recommendation: string;
  confidence_score: number;
  analysis: string;
}

// Watchlist interfaces
export interface WatchlistStock {
  symbol: string;
  name: string;
  price: number;
  change_percent: number;
}

export interface Watchlist {
  id: number;
  name: string;
  stocks: WatchlistStock[];
}

// Sentiment interfaces
export interface SentimentSource {
  news: number;
  social_media: number;
  analyst_ratings: number;
}

export interface SentimentChanges {
  '1_day': number;
  '1_week': number;
  '1_month': number;
}

export interface StockSentiment {
  symbol: string;
  overall_sentiment: string;
  sentiment_score: number;
  date: string;
  sources: SentimentSource;
  recent_changes: SentimentChanges;
}

// Market data interfaces
export interface MarketIndex {
  name: string;
  value: number;
  change_percent: number;
}

export interface MarketSector {
  name: string;
  change_percent: number;
}

export interface MarketOverview {
  date: string;
  indices: MarketIndex[];
  sectors: MarketSector[];
  market_sentiment: string;
  volatility_index: number;
}

// Backtest interfaces
export interface BacktestResult {
  id: string;
  symbol: string;
  strategy: string;
  strategy_id: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  final_value: number;
  total_return: number;
  annualized_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  trades: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  volatility: number;
  created_at: string;
}

export interface BacktestRequest {
  symbol: string;
  strategy: string;
  strategy_id: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  parameters?: Record<string, any>;
}

// Portfolio interfaces
export interface Position {
  id: number;
  symbol: string;
  name: string;
  shares: number; // Changed from quantity to shares
  purchase_price: number;
  current_price: number;
  change_percent: number;
  market_value: number;
  profit_loss: number;
}

export interface Portfolio {
  id: number;
  name: string;
  total_value: number;
  cash_balance: number;
  daily_change_percent: number;
  total_profit_loss: number;
  total_profit_loss_percent: number;
  positions: Position[];
}

// Alert interfaces
export interface Alert {
  id: number;
  symbol: string;
  type: string;
  condition: string;
  value: number;
  current_price?: number;
  status: string;
  triggered: boolean;
  created_at: string;
  triggered_at?: string;
}

export interface CreateAlertRequest {
  symbol: string;
  type: string;
  condition: string;
  value: number;
  message?: string;
}

// News interfaces
export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  content: string;
  url: string;
  source: string;
  author: string;
  category: string;
  published_at: string;
  sentiment: string;
  relevance?: number;
  symbols?: string[];
}

class ApiService {
  // Stock methods
  async getTrendingStocks(): Promise<Stock[]> {
    const response = await apiClient.get<StandardResponse<Stock[]>>(
      API_ENDPOINTS.STOCKS.TRENDING
    );
    return response.data.data;
  }

  async getStockDetails(symbol: string): Promise<Stock> {
    const response = await apiClient.get<StandardResponse<Stock>>(
      API_ENDPOINTS.STOCKS.DETAILS(symbol)
    );
    return response.data.data;
  }

  async searchStocks(query: string): Promise<Stock[]> {
    const response = await apiClient.get<StandardResponse<Stock[]>>(
      `${API_ENDPOINTS.STOCKS.SEARCH}?q=${encodeURIComponent(query)}`
    );
    return response.data.data;
  }

  // Prediction methods
  async getStockPrediction(symbol: string): Promise<StockPrediction> {
    const response = await apiClient.get<StandardResponse<StockPrediction>>(
      API_ENDPOINTS.PREDICTIONS.GET(symbol)
    );
    return response.data.data;
  }

  async getAdvancedPrediction(symbol: string, days: number = 30, model: string = 'standard'): Promise<StockPrediction> {
    const response = await apiClient.get<StandardResponse<StockPrediction>>(
      `${API_ENDPOINTS.PREDICTIONS.ADVANCED}?symbol=${encodeURIComponent(symbol)}&days=${days}&model=${model}`
    );
    return response.data.data;
  }

  async getPreMarketPrediction(symbol: string): Promise<StockPrediction> {
    const response = await apiClient.get<StandardResponse<StockPrediction>>(
      API_ENDPOINTS.PREDICTIONS.PRE_MARKET(symbol)
    );
    return response.data.data;
  }

  // Sentiment methods
  async getStockSentiment(symbol: string): Promise<StockSentiment> {
    const response = await apiClient.get<StandardResponse<StockSentiment>>(
      API_ENDPOINTS.SENTIMENT.GET(symbol)
    );
    return response.data.data;
  }

  async getSentimentHistory(symbol: string, days: number = 30): Promise<{ date: string; score: number }[]> {
    const response = await apiClient.get<StandardResponse<{ date: string; score: number }[]>>(
      `${API_ENDPOINTS.SENTIMENT.HISTORY(symbol)}?days=${days}`
    );
    return response.data.data;
  }

  // Analytics methods
  async getMarketOverview(): Promise<MarketOverview> {
    const response = await apiClient.get<StandardResponse<MarketOverview>>(
      API_ENDPOINTS.ANALYTICS.MARKET_OVERVIEW
    );
    return response.data.data;
  }

  async getSectorPerformance(): Promise<MarketSector[]> {
    const response = await apiClient.get<StandardResponse<MarketSector[]>>(
      API_ENDPOINTS.ANALYTICS.SECTORS
    );
    return response.data.data;
  }

  async getTopMovers(): Promise<Stock[]> {
    const response = await apiClient.get<StandardResponse<Stock[]>>(
      API_ENDPOINTS.ANALYTICS.TOP_MOVERS
    );
    return response.data.data;
  }

  async getPredictiveAnalytics(
    symbols: string[],
    horizon = '1w',
    confidenceLevel = 0.95
  ): Promise<any> {
    const params = new URLSearchParams({
      symbols: symbols.join(','),
      horizon,
      confidence_level: confidenceLevel.toString()
    });
    const response = await apiClient.get<StandardResponse<any>>(
      `${API_ENDPOINTS.ANALYTICS.PREDICTIVE}?${params.toString()}`
    );
    return response.data.data;
  }

  // Backtest methods
  async runBacktest(backtestRequest: BacktestRequest): Promise<BacktestResult> {
    const response = await apiClient.post<StandardResponse<BacktestResult>>(
      API_ENDPOINTS.BACKTEST.RUN,
      backtestRequest
    );
    return response.data.data;
  }

  async getBacktestHistory(): Promise<BacktestResult[]> {
    const response = await apiClient.get<StandardResponse<BacktestResult[]>>(
      API_ENDPOINTS.BACKTEST.HISTORY
    );
    return response.data.data;
  }

  // Portfolio methods
  async getPortfolios(): Promise<Portfolio[]> {
    const response = await apiClient.get<StandardResponse<Portfolio[]>>(
      API_ENDPOINTS.PORTFOLIO.LIST
    );
    return response.data.data;
  }

  async createPortfolio(portfolioData: { name: string; description?: string }): Promise<Portfolio> {
    const response = await apiClient.post<StandardResponse<Portfolio>>(
      API_ENDPOINTS.PORTFOLIO.CREATE,
      portfolioData
    );
    return response.data.data;
  }

  async getPortfolioById(id: number): Promise<Portfolio> {
    const response = await apiClient.get<StandardResponse<Portfolio>>(
      API_ENDPOINTS.PORTFOLIO.GET(id)
    );
    return response.data.data;
  }

  async addPosition(portfolioId: number, positionData: { symbol: string; shares: number; purchase_price: number }): Promise<Position> {
    const response = await apiClient.post<StandardResponse<Position>>(
      API_ENDPOINTS.PORTFOLIO.ADD_POSITION(portfolioId),
      positionData
    );
    return response.data.data;
  }

  async removePosition(portfolioId: number, positionId: number): Promise<void> {
    await apiClient.delete(
      API_ENDPOINTS.PORTFOLIO.DELETE_POSITION(portfolioId, positionId)
    );
  }

  async updatePosition(portfolioId: number, positionId: number, quantity: number): Promise<Position> {
    const response = await apiClient.put<StandardResponse<Position>>(
      API_ENDPOINTS.PORTFOLIO.UPDATE_POSITION(portfolioId, positionId),
      { quantity }
    );
    return response.data.data;
  }

  // Watchlist methods
  async getWatchlists(): Promise<Watchlist[]> {
    const response = await apiClient.get<StandardResponse<Watchlist[]>>(
      API_ENDPOINTS.WATCHLISTS.LIST
    );
    return response.data.data;
  }

  async createWatchlist(watchlistData: { name: string }): Promise<Watchlist> {
    const response = await apiClient.post<StandardResponse<Watchlist>>(
      API_ENDPOINTS.WATCHLISTS.CREATE,
      watchlistData
    );
    return response.data.data;
  }

  async deleteWatchlist(id: number): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.WATCHLISTS.DELETE(id));
  }

  async addToWatchlist(watchlistId: number, symbol: string): Promise<void> {
    await apiClient.post(
      API_ENDPOINTS.WATCHLISTS.ADD(watchlistId),
      { symbol }
    );
  }

  async removeFromWatchlist(watchlistId: number, symbol: string): Promise<void> {
    await apiClient.delete(
      API_ENDPOINTS.WATCHLISTS.REMOVE(watchlistId, symbol)
    );
  }

  // Alert methods
  async getAlerts(): Promise<Alert[]> {
    const response = await apiClient.get<StandardResponse<Alert[]>>(
      API_ENDPOINTS.ALERTS.LIST
    );
    return response.data.data;
  }

  async createAlert(alertData: CreateAlertRequest): Promise<Alert> {
    const response = await apiClient.post<StandardResponse<Alert>>(
      API_ENDPOINTS.ALERTS.CREATE,
      alertData
    );
    return response.data.data;
  }

  async deleteAlert(alertId: number): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.ALERTS.DELETE(alertId));
  }

  // News methods
  async getLatestNews(limit: number = 10): Promise<NewsItem[]> {
    const response = await apiClient.get<StandardResponse<NewsItem[]>>(
      `${API_ENDPOINTS.NEWS.LATEST}?limit=${limit}`
    );
    return response.data.data;
  }

  async getStockNews(symbol: string, limit: number = 10): Promise<NewsItem[]> {
    const response = await apiClient.get<StandardResponse<NewsItem[]>>(
      `${API_ENDPOINTS.NEWS.STOCK(symbol)}?limit=${limit}`
    );
    return response.data.data;
  }

  // Preference methods
  async getUserPreferences() {
    const response = await apiClient.get<StandardResponse<any>>(
      API_ENDPOINTS.PREFERENCES.GET
    );
    return response.data.data;
  }

  async updateUserPreferences(prefs: any) {
    const response = await apiClient.put<StandardResponse<any>>(
      API_ENDPOINTS.PREFERENCES.UPDATE,
      prefs
    );
    return response.data.data;
  }

  async updateTheme(theme: string) {
    const response = await apiClient.put<StandardResponse<any>>(
      API_ENDPOINTS.PREFERENCES.THEME,
      { theme }
    );
    return response.data.data;
  }

  async updateNotificationSettings(settings: any) {
    const response = await apiClient.put<StandardResponse<any>>(
      API_ENDPOINTS.PREFERENCES.NOTIFICATIONS,
      settings
    );
    return response.data.data;
  }

  // AI methods
  async chatWithAI(message: string) {
    const response = await apiClient.post<StandardResponse<any>>(
      API_ENDPOINTS.AI.CHAT,
      { message }
    );
    return response.data.data;
  }

  async analyzeText(text: string) {
    const response = await apiClient.post<StandardResponse<any>>(
      API_ENDPOINTS.AI.ANALYZE,
      { text }
    );
    return response.data.data;
  }

  async generateStrategy(data: any) {
    const response = await apiClient.post<StandardResponse<any>>(
      API_ENDPOINTS.AI.STRATEGY,
      data
    );
    return response.data.data;
  }

  async getPortfolioSuggestion(data: any) {
    const response = await apiClient.post<StandardResponse<any>>(
      API_ENDPOINTS.AI.PORTFOLIO_SUGGESTION,
      data
    );
    return response.data.data;
  }

  // Performance monitoring
  getApiPerformanceMetrics() {
    return {
      responseTime: apiClient.getResponseTime(),
      endpointPerformance: getEndpointPerformance(),
    };
  }
}

// Helper function for performance metrics
function getEndpointPerformance() {
  // In a real implementation, this would track response times by endpoint
  return {};
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;