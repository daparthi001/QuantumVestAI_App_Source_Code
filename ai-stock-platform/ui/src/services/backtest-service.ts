/**
 * Backtesting Service
 * Created: 2025-06-19 03:09:13
 * Author: daparthi001
 */
import { api } from './api';

export interface BacktestParameters {
  // Portfolio settings
  initialCapital: number;
  symbols: string[];
  weights?: Record<string, number>;
  
  // Time period
  startDate: string;
  endDate: string;
  
  // Strategy parameters
  strategy: 'buy_and_hold' | 'rebalance' | 'momentum' | 'mean_reversion' | 'custom';
  rebalanceFrequency?: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  
  // Risk management
  stopLoss?: number;
  takeProfit?: number;
  maxDrawdown?: number;
  
  // Advanced settings
  transactionFee?: number;
  slippage?: number;
  
  // Custom strategy configuration
  customStrategy?: {
    entryConditions: string[];
    exitConditions: string[];
    positionSizing: string;
    riskParameters: Record<string, any>;
  }
}

export interface BacktestResult {
  id: string;
  parameters: BacktestParameters;
  results: {
    // Performance metrics
    totalReturn: number;
    annualizedReturn: number;
    sharpeRatio: number;
    sortino: number;
    maxDrawdown: number;
    volatility: number;
    beta: number;
    alpha: number;
    
    // Detailed performance
    equityCurve: Array<{date: string, value: number}>;
    monthlyReturns: Record<string, number>;
    trades: Array<{
      symbol: string;
      entryDate: string;
      entryPrice: number;
      exitDate: string;
      exitPrice: number;
      return: number;
      holdingPeriod: number;
    }>;
    
    // Position data
    positions: Record<string, Array<{date: string, value: number}>>;
    
    // Benchmark comparison
    benchmarkReturn: number;
    benchmarkCurve: Array<{date: string, value: number}>;
    
    // Risk metrics
    drawdowns: Array<{start: string, end: string, depth: number, recovery: string}>;
    riskMetrics: Record<string, number>;
  };
  created: string;
  status: 'completed' | 'running' | 'failed';
}

export const backtestService = {
  /**
   * Run a new backtest
   */
  async runBacktest(parameters: BacktestParameters): Promise<{ id: string }> {
    try {
      const response = await api.post('/backtest', parameters);
      return response.data.data;
    } catch (error) {
      console.error('Error running backtest:', error);
      throw error;
    }
  },

  /**
   * Get backtest result by ID
   */
  async getBacktestResult(id: string): Promise<BacktestResult> {
    try {
      const response = await api.get(`/backtest/${id}`);
      return response.data.data;
    } catch (error) {
      console.error(`Error fetching backtest result ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get all backtest results for the current user
   */
  async getUserBacktests(): Promise<BacktestResult[]> {
    try {
      const response = await api.get('/backtest/user');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching user backtests:', error);
      throw error;
    }
  },

  /**
   * Delete a backtest by ID
   */
  async deleteBacktest(id: string): Promise<void> {
    try {
      await api.delete(`/backtest/${id}`);
    } catch (error) {
      console.error(`Error deleting backtest ${id}:`, error);
      throw error;
    }
  },

  /**
   * Compare multiple backtests
   */
  async compareBacktests(ids: string[]): Promise<any> {
    try {
      const response = await api.post('/backtest/compare', { ids });
      return response.data.data;
    } catch (error) {
      console.error('Error comparing backtests:', error);
      throw error;
    }
  }
};