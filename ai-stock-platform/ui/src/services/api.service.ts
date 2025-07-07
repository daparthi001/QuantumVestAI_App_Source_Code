/**
 * Unified API Service
 * Created: 2025-06-19 17:56:46
 * Author: daparthi001
 */
import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import authService from './auth.service';

class ApiService {
  private apiClient: AxiosInstance;
  
  constructor() {
    // Get API base URL from environment or derive from window location
    const apiBaseUrl = process.env.REACT_APP_API_URL || 
                      window.location.protocol + '//' + window.location.hostname + 
                      (window.location.hostname === 'localhost' ? ':8000' : '');
    
    // Create axios instance
    this.apiClient = axios.create({
      baseURL: apiBaseUrl,
      timeout: 30000, // 30 second timeout
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    // Add request interceptor to attach auth token
    this.apiClient.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = authService.getToken();
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error: AxiosError) => Promise.reject(error)
    );
    
    // Add response interceptor to handle errors
    this.apiClient.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        this.handleApiError(error);
        return Promise.reject(error);
      }
    );
  }
  
  // Handle common API errors
  private handleApiError(error: AxiosError): void {
    if (error.response) {
      const status = error.response.status;
      
      // Handle unauthorized errors (token expired or invalid)
      if (status === 401) {
        console.error('Authentication error. Please log in again.');
        authService.logout();
        window.location.href = '/login';
      } 
      // Handle forbidden errors (insufficient permissions)
      else if (status === 403) {
        console.error('You do not have permission to access this resource.');
      }
      // Handle server errors
      else if (status >= 500) {
        console.error('Server error. Please try again later.');
      }
    } else if (error.request) {
      // Request made but no response received (network issue)
      console.error('Network error. Please check your connection.');
    } else {
      // Error setting up request
      console.error('Error:', error.message);
    }
  }
  
  // Generic GET method
  async get<T>(endpoint: string, params?: any): Promise<T> {
    try {
      const response = await this.apiClient.get<{ status: string, data: T }>(endpoint, { params });
      return response.data.data;
    } catch (error) {
      console.error(`GET ${endpoint} failed:`, error);
      throw error;
    }
  }
  
  // Generic POST method
  async post<T>(endpoint: string, data: any): Promise<T> {
    try {
      const response = await this.apiClient.post<{ status: string, data: T }>(endpoint, data);
      return response.data.data;
    } catch (error) {
      console.error(`POST ${endpoint} failed:`, error);
      throw error;
    }
  }
  
  // Generic PUT method
  async put<T>(endpoint: string, data: any): Promise<T> {
    try {
      const response = await this.apiClient.put<{ status: string, data: T }>(endpoint, data);
      return response.data.data;
    } catch (error) {
      console.error(`PUT ${endpoint} failed:`, error);
      throw error;
    }
  }
  
  // Generic DELETE method
  async delete<T>(endpoint: string, params?: any): Promise<T> {
    try {
      const response = await this.apiClient.delete<{ status: string, data: T }>(endpoint, { params });
      return response.data.data;
    } catch (error) {
      console.error(`DELETE ${endpoint} failed:`, error);
      throw error;
    }
  }
  
  // Stock API methods
  async getTrendingStocks() {
    return this.get('/api/v1/stocks/trending');
  }
  
  async getStockDetails(symbol: string) {
    return this.get(`/api/v1/stocks/${symbol}`);
  }
  
  // Prediction API methods
  async getStockPrediction(symbol: string) {
    return this.get(`/api/v1/predictions/${symbol}`);
  }
  
  // Watchlist API methods
  async getWatchlists() {
    return this.get('/api/v1/watchlists');
  }
  
  // Sentiment API methods
  async getStockSentiment(symbol: string) {
    return this.get(`/api/v1/sentiment/${symbol}`);
  }
  
  // Analytics API methods
  async getMarketOverview() {
    return this.get('/api/v1/analytics/market-overview');
  }
  
  // Backtest API methods
  async runBacktest(backtestData: any) {
    return this.post('/api/v1/backtest', backtestData);
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;