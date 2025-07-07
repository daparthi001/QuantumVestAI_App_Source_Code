/**
 * Portfolio Types
 * Created: 2025-01-08
 * Author: daparthi001
 */

export interface Position {
  symbol: string;
  shares: number;
  averagePrice: number;
  currentPrice: number;
  totalValue: number;
  gainLoss: number;
  gainLossPercent: number;
  type: 'LONG' | 'SHORT';
  // Additional properties required by the system
  costBasis: number;
  averageCost: number;
  priceChange: number;
  priceChangePercent: number;
  marketValue: number;
}

export interface Transaction {
  id: string;
  symbol: string;
  type: 'BUY' | 'SELL';
  shares: number;
  price: number;
  total: number;
  timestamp: string;
  fees?: number;
}

export interface PortfolioSummary {
  totalValue: number;
  totalGainLoss: number;
  totalGainLossPercent: number;
  cash: number;
  positions: Position[];
  dayChange: number;
  dayChangePercent: number;
  // Additional property required by the system
  cashBalance: number;
}

export interface PortfolioPerformance {
  date: string;
  value: number;
  return: number;
  returnPercent: number;
}

export interface PortfolioMetrics {
  totalReturn: number;
  totalReturnPercent: number;
  sharpeRatio: number;
  maxDrawdown: number;
  volatility: number;
  beta: number;
}