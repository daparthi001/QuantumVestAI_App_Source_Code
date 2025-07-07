/**
 * Advanced API Service
 * Updated: 2025-06-19 18:06:43
 * Author: daparthi001
 */
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { API_BASE_URL } from '../config/constants';
import authService from './auth.service';

// Extend AxiosInstance to include custom methods
interface ExtendedAxiosInstance extends AxiosInstance {
  getResponseTime(): {
    average: number;
    max: number;
    min: number;
  };
}

// API request queue for handling 401 token refresh
let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

// Create a custom API client with advanced features
const apiClient: ExtendedAxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
}) as ExtendedAxiosInstance;

// Request interceptor with advanced features
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get token and add it to the request
    const token = authService.getToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add request timestamp for performance monitoring
    if (config.headers) {
      config.headers['X-Request-Time'] = Date.now().toString();
    }
    
    // Add device info for analytics
    if (config.headers) {
      config.headers['X-Device-Type'] = 'web';
      config.headers['X-App-Version'] = '1.0.1';
    }
    
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Advanced response interceptor with token refresh, rate limiting handling, and retry logic
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Calculate and log response time
    const requestTime = response.config.headers?.['X-Request-Time'];
    if (requestTime) {
      const responseTime = Date.now() - parseInt(requestTime.toString(), 10);
      console.debug(`API call to ${response.config.url} took ${responseTime}ms`);
      
      // Add response time to response headers
      response.headers['X-Response-Time'] = responseTime.toString();
    }
    
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    if (error.response) {
      // Handle 401 Unauthorized errors with token refresh
      if (error.response.status === 401 && !originalRequest._retry) {
        if (isRefreshing) {
          // If token refresh is in progress, queue this request
          try {
            const token = await new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject });
            });
            
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            
            return axios(originalRequest);
          } catch (err) {
            return Promise.reject(err);
          }
        }
        
        originalRequest._retry = true;
        isRefreshing = true;
        
        try {
          // Try to refresh token logic would go here in a real implementation
          // For now, just logout since we don't have refresh token functionality
          authService.logout();
          processQueue(new Error('Token refresh failed'));
          window.location.href = '/login';
          return Promise.reject(error);
        } catch (refreshError) {
          processQueue(refreshError);
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }
      
      // Handle 403 Forbidden errors
      if (error.response.status === 403) {
        console.error('Permission denied for this resource');
      }
      
      // Handle 404 Not Found errors
      if (error.response.status === 404) {
        console.error('Resource not found');
      }
      
      // Handle 429 Too Many Requests (rate limiting)
      if (error.response.status === 429) {
        const retryAfter = error.response.headers['retry-after'] 
          ? parseInt(error.response.headers['retry-after'] as string, 10) * 1000 
          : 5000;
          
        console.warn(`Rate limited. Retrying after ${retryAfter}ms`);
        await new Promise(resolve => setTimeout(resolve, retryAfter));
        
        // Retry the request
        return axios(originalRequest);
      }
      
      // Handle 500 Internal Server Error
      if (error.response.status === 500) {
        console.error('Server error occurred');
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received from server');
      
      // Implement retry logic for network issues
      if (!originalRequest._retry && navigator.onLine) {
        originalRequest._retry = true;
        console.warn('Network issue detected. Retrying request...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        return axios(originalRequest);
      }
    } else {
      // Something happened in setting up the request
      console.error('Error setting up request', error.message);
    }
    
    return Promise.reject(error);
  }
);

// Add response time tracking method
apiClient.getResponseTime = () => {
  return {
    average: calculateAverageResponseTime(),
    max: getMaxResponseTime(),
    min: getMinResponseTime()
  };
};

// Track response times
const responseTimes: Record<string, number[]> = {};

function trackResponseTime(endpoint: string, time: number) {
  if (!responseTimes[endpoint]) {
    responseTimes[endpoint] = [];
  }
  
  responseTimes[endpoint].push(time);
  
  // Keep only last 100 requests
  if (responseTimes[endpoint].length > 100) {
    responseTimes[endpoint].shift();
  }
}

function calculateAverageResponseTime() {
  const allTimes: number[] = [];
  Object.values(responseTimes).forEach(times => {
    allTimes.push(...times);
  });
  
  if (allTimes.length === 0) return 0;
  
  return allTimes.reduce((sum, time) => sum + time, 0) / allTimes.length;
}

function getMaxResponseTime() {
  const allTimes: number[] = [];
  Object.values(responseTimes).forEach(times => {
    allTimes.push(...times);
  });
  
  if (allTimes.length === 0) return 0;
  
  return Math.max(...allTimes);
}

function getMinResponseTime() {
  const allTimes: number[] = [];
  Object.values(responseTimes).forEach(times => {
    allTimes.push(...times);
  });
  
  if (allTimes.length === 0) return 0;
  
  return Math.min(...allTimes);
}

export default apiClient;
export { apiClient as api }; // Export as named export for compatibility

// Export additional services
export { default as stockService } from './stock.service';
export { default as portfolioService } from './portfolio.service';
export { orderApi } from './api/orderApi';