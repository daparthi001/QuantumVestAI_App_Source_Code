/**
 * Advanced Application Constants
 * Updated: 2025-06-19 18:06:43
 * Author: daparthi001
 */

// API configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://dev.quantumvestai.com';

// Authentication
export const ACCESS_TOKEN_KEY = 'qvai_token';

// API Endpoints
export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    LOGOUT: '/api/v1/auth/logout',
    CURRENT_USER: '/api/v1/auth/me',
    FORGOT_PASSWORD: '/api/v1/auth/password-reset/request',
    RESET_PASSWORD: '/api/v1/auth/password-reset/confirm',
  },
  // Stock endpoints
  STOCKS: {
    TRENDING: '/api/v1/stocks/trending',
    DETAILS: (symbol: string) => `/api/v1/stocks/${symbol}`,
    SEARCH: '/api/v1/stocks/search',
    HISTORY: (symbol: string) => `/api/v1/stocks/${symbol}/history`,
    FUNDAMENTALS: (symbol: string) => `/api/v1/stocks/${symbol}/fundamentals`,
    EARNINGS: (symbol: string) => `/api/v1/stocks/${symbol}/earnings`,
    COMPETITORS: (symbol: string) => `/api/v1/stocks/${symbol}/competitors`,
    RECOMMENDATIONS: (symbol: string) => `/api/v1/stocks/${symbol}/recommendations`,
  },
  // Prediction endpoints
  PREDICTIONS: {
    GET: (symbol: string) => `/api/v1/predictions/${symbol}`,
    ADVANCED: '/api/v1/predictions/advanced',
    COMPARISON: '/api/v1/predictions/comparison',
    ACCURACY: '/api/v1/predictions/accuracy',
    MODELS: '/api/v1/predictions/models',
  },
  // Watchlist endpoints
  WATCHLISTS: {
    LIST: '/api/v1/watchlists',
    CREATE: '/api/v1/watchlists',
    GET: (id: number) => `/api/v1/watchlists/${id}`,
    UPDATE: (id: number) => `/api/v1/watchlists/${id}`,
    DELETE: (id: number) => `/api/v1/watchlists/${id}`,
    ADD: (id: number) => `/api/v1/watchlists/${id}/add`,
    REMOVE: (id: number, symbol: string) => `/api/v1/watchlists/${id}/remove/${symbol}`,
  },
  // Sentiment endpoints
  SENTIMENT: {
    GET: (symbol: string) => `/api/v1/sentiment/${symbol}`,
    HISTORY: (symbol: string) => `/api/v1/sentiment/${symbol}/history`,
    SOCIAL: (symbol: string) => `/api/v1/sentiment/${symbol}/social`,
    NEWS: (symbol: string) => `/api/v1/sentiment/${symbol}/news`,
    ANALYST: (symbol: string) => `/api/v1/sentiment/${symbol}/analyst`,
  },
  // Analytics endpoints
  ANALYTICS: {
    MARKET_OVERVIEW: '/api/v1/analytics/market-overview',
    SECTORS: '/api/v1/analytics/sectors',
    TOP_MOVERS: '/api/v1/analytics/top-movers',
    PREDICTIVE: '/api/v1/analytics/predictive',
    MARKET_BREADTH: '/api/v1/analytics/market-breadth',
    ECONOMIC_INDICATORS: '/api/v1/analytics/economic-indicators',
    CORRELATIONS: '/api/v1/analytics/correlations',
    RISK_ANALYSIS: '/api/v1/analytics/risk-analysis',
  },
  // Backtest endpoints
  BACKTEST: {
    RUN: '/api/v1/backtest',
    HISTORY: '/api/v1/backtest/history',
    GET: (id: string) => `/api/v1/backtest/${id}`,
    COMPARE: '/api/v1/backtest/compare',
    STRATEGIES: '/api/v1/backtest/strategies',
    OPTIMIZE: '/api/v1/backtest/optimize',
  },
  // Portfolio endpoints
  PORTFOLIO: {
    LIST: '/api/v1/portfolios',
    CREATE: '/api/v1/portfolios',
    GET: (id: number) => `/api/v1/portfolios/${id}`,
    UPDATE: (id: number) => `/api/v1/portfolios/${id}`,
    DELETE: (id: number) => `/api/v1/portfolios/${id}`,
    PERFORMANCE: (id: number) => `/api/v1/portfolios/${id}/performance`,
    RISK: (id: number) => `/api/v1/portfolios/${id}/risk`,
    ALLOCATION: (id: number) => `/api/v1/portfolios/${id}/allocation`,
    ADD_POSITION: (id: number) => `/api/v1/portfolios/${id}/positions`,
    UPDATE_POSITION: (portfolioId: number, positionId: number) => `/api/v1/portfolios/${portfolioId}/positions/${positionId}`,
    DELETE_POSITION: (portfolioId: number, positionId: number) => `/api/v1/portfolios/${portfolioId}/positions/${positionId}`,
  },
  // Alert endpoints
  ALERTS: {
    LIST: '/api/v1/alerts',
    CREATE: '/api/v1/alerts',
    GET: (id: number) => `/api/v1/alerts/${id}`,
    UPDATE: (id: number) => `/api/v1/alerts/${id}`,
    DELETE: (id: number) => `/api/v1/alerts/${id}`,
    HISTORY: '/api/v1/alerts/history',
    TRIGGERED: '/api/v1/alerts/triggered',
  },
  // News endpoints
  NEWS: {
    LATEST: '/api/v1/news',
    STOCK: (symbol: string) => `/api/v1/news/stock/${symbol}`,
    SECTOR: (sector: string) => `/api/v1/news/sector/${sector}`,
    SEARCH: '/api/v1/news/search',
    TRENDING: '/api/v1/news/trending',
  },
  // User preferences endpoints
  PREFERENCES: {
    GET: '/api/v1/preferences',
    UPDATE: '/api/v1/preferences',
    THEME: '/api/v1/preferences/theme',
    NOTIFICATIONS: '/api/v1/preferences/notifications',
  },
  // Advanced AI features
  AI: {
    CHAT: '/api/v1/ai/chat',
    ANALYZE: '/api/v1/ai/analyze',
    STRATEGY: '/api/v1/ai/strategy',
    PORTFOLIO_SUGGESTION: '/api/v1/ai/portfolio-suggestion',
  },
};

// Local storage keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'qvai_token',
  USER_DATA: 'qvai_user',
  THEME: 'qvai_theme',
  LANGUAGE: 'qvai_lang',
  PREFERENCES: 'qvai_prefs',
  RECENT_SEARCHES: 'qvai_recent_searches',
  LAST_VISITED: 'qvai_last_visited',
  TUTORIAL_COMPLETED: 'qvai_tutorial_completed',
};

// Application routes
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
  DASHBOARD: '/dashboard',
  STOCKS: '/stocks',
  STOCK_FLOW: '/stocks/flow',
  WATCHLIST: '/watchlist',
  ANALYTICS: '/analytics',
  SETTINGS: '/settings',
  PROFILE: '/profile',
  PORTFOLIO: '/portfolio',
  BACKTEST: '/backtest',
  PREDICTIONS: '/predictions',
  NEWS: '/news',
  ALERTS: '/alerts',
  AI_ASSISTANT: '/ai-assistant',
  TRADING: '/trading',
  REPORTS: '/reports',
  INTEGRATIONS: '/integrations',
};

// Chart configurations
export const CHART_CONFIGS = {
  THEMES: {
    LIGHT: {
      backgroundColor: '#ffffff',
      textColor: '#333333',
      gridColor: '#e0e0e0',
      lineColors: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
    },
    DARK: {
      backgroundColor: '#2d2d2d',
      textColor: '#e0e0e0',
      gridColor: '#444444',
      lineColors: ['#4bb2c5', '#c5b47f', '#EAA228', '#579575', '#839557'],
    },
  },
  TIME_PERIODS: [
    { label: '1D', value: '1d' },
    { label: '1W', value: '1w' },
    { label: '1M', value: '1m' },
    { label: '3M', value: '3m' },
    { label: '6M', value: '6m' },
    { label: 'YTD', value: 'ytd' },
    { label: '1Y', value: '1y' },
    { label: '5Y', value: '5y' },
    { label: 'MAX', value: 'max' },
  ],
};

// Feature flags for progressive enhancement
export const FEATURE_FLAGS = {
  ADVANCED_ANALYTICS: true,
  AI_ASSISTANT: true,
  PORTFOLIO_OPTIMIZATION: true,
  SOCIAL_SENTIMENT: true,
  STRATEGY_BACKTESTING: true,
  DARK_MODE: true,
  REAL_TIME_DATA: true,
  PUSH_NOTIFICATIONS: true,
};