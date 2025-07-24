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

  // Preference methods
  getUserPreferences: typeof apiService.getUserPreferences;
  updateUserPreferences: typeof apiService.updateUserPreferences;
  updateTheme: typeof apiService.updateTheme;
  updateNotificationSettings: typeof apiService.updateNotificationSettings;

  // AI methods
  chatWithAI: typeof apiService.chatWithAI;
  analyzeText: typeof apiService.analyzeText;
  generateStrategy: typeof apiService.generateStrategy;
  getPortfolioSuggestion: typeof apiService.getPortfolioSuggestion;
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
  getUserPreferences: apiService.getUserPreferences.bind(apiService),
  updateUserPreferences: apiService.updateUserPreferences.bind(apiService),
  updateTheme: apiService.updateTheme.bind(apiService),
  updateNotificationSettings: apiService.updateNotificationSettings.bind(apiService),
  chatWithAI: apiService.chatWithAI.bind(apiService),
  analyzeText: apiService.analyzeText.bind(apiService),
  generateStrategy: apiService.generateStrategy.bind(apiService),
  getPortfolioSuggestion: apiService.getPortfolioSuggestion.bind(apiService),
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
    getUserPreferences: apiService.getUserPreferences.bind(apiService),
    updateUserPreferences: apiService.updateUserPreferences.bind(apiService),
    updateTheme: apiService.updateTheme.bind(apiService),
    updateNotificationSettings: apiService.updateNotificationSettings.bind(apiService),
    chatWithAI: apiService.chatWithAI.bind(apiService),
    analyzeText: apiService.analyzeText.bind(apiService),
    generateStrategy: apiService.generateStrategy.bind(apiService),
    getPortfolioSuggestion: apiService.getPortfolioSuggestion.bind(apiService),
  };

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
};

// Hook to use API context
export const useApi = (): ApiContextType => {
  return useContext(ApiContext);
};