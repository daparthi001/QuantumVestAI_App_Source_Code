/**
 * API Context
 * Created: 2025-06-19 17:56:46
 * Author: daparthi001
 */
import React, { createContext, useContext, ReactNode } from 'react';
import apiService from '../services/api.service';

// API Context type
interface ApiContextType {
  // Stock methods
  getTrendingStocks: typeof apiService.getTrendingStocks;
  getStockDetails: typeof apiService.getStockDetails;
  
  // Prediction methods
  getStockPrediction: typeof apiService.getStockPrediction;
  
  // Watchlist methods
  getWatchlists: typeof apiService.getWatchlists;
  
  // Sentiment methods
  getStockSentiment: typeof apiService.getStockSentiment;
  
  // Analytics methods
  getMarketOverview: typeof apiService.getMarketOverview;
  
  // Backtest methods
  runBacktest: typeof apiService.runBacktest;
}

// Create context with default values
const ApiContext = createContext<ApiContextType>({
  getTrendingStocks: apiService.getTrendingStocks.bind(apiService),
  getStockDetails: apiService.getStockDetails.bind(apiService),
  getStockPrediction: apiService.getStockPrediction.bind(apiService),
  getWatchlists: apiService.getWatchlists.bind(apiService),
  getStockSentiment: apiService.getStockSentiment.bind(apiService),
  getMarketOverview: apiService.getMarketOverview.bind(apiService),
  runBacktest: apiService.runBacktest.bind(apiService),
});

// Props interface for the provider
interface ApiProviderProps {
  children: ReactNode;
}

// API Provider component
export const ApiProvider: React.FC<ApiProviderProps> = ({ children }) => {
  // Context value with bound methods
  const value: ApiContextType = {
    getTrendingStocks: apiService.getTrendingStocks.bind(apiService),
    getStockDetails: apiService.getStockDetails.bind(apiService),
    getStockPrediction: apiService.getStockPrediction.bind(apiService),
    getWatchlists: apiService.getWatchlists.bind(apiService),
    getStockSentiment: apiService.getStockSentiment.bind(apiService),
    getMarketOverview: apiService.getMarketOverview.bind(apiService),
    runBacktest: apiService.runBacktest.bind(apiService),
  };

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
};

// Hook to use API context
export const useApi = (): ApiContextType => {
  return useContext(ApiContext);
};