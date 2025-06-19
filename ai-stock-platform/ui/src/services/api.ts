/**
 * API Service
 * Created: 2025-05-19 04:05:44
 * Updated: 2025-06-19 03:05:06
 * Author: daparthi001
 */
import axios, { AxiosError } from 'axios';

// Use relative URL to avoid CORS issues
const API_BASE_URL = '/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        // Log detailed error information
        console.error('API Error:', error.response?.data || error.message);
        console.error('Request URL:', error.config?.url);
        console.error('Request Method:', error.config?.method);
        
        const status = error.response?.status;
        
        // Handle authentication errors
        if (status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login?session_expired=true';
        }
        
        // Handle API service unavailable
        if (status === 503) {
            console.error('API Service Unavailable');
        }
        
        // Handle rate limiting
        if (status === 429) {
            console.error('Too many requests, please try again later');
        }
        
        return Promise.reject(error);
    }
);

export const stockService = {
    async getStockData(symbol: string) {
        try {
            const response = await api.get(`/stocks/${symbol}`);
            return response.data;
        } catch (error) {
            console.error(`Error fetching stock data for ${symbol}:`, error);
            throw error;
        }
    },

    async getHistoricalPrices(symbol: string, startDate: string, endDate: string) {
        try {
            const response = await api.get(`/stocks/${symbol}/prices`, {
                params: { start_date: startDate, end_date: endDate }
            });
            return response.data;
        } catch (error) {
            console.error(`Error fetching historical prices for ${symbol}:`, error);
            throw error;
        }
    },

    async getTechnicalIndicators(symbol: string, indicators: string[]) {
        try {
            const response = await api.get(`/stocks/${symbol}/indicators`, {
                params: { indicators: indicators.join(',') }
            });
            return response.data;
        } catch (error) {
            console.error(`Error fetching technical indicators for ${symbol}:`, error);
            throw error;
        }
    }
};

export const authService = {
    async login(username: string, password: string) {
        try {
            const response = await api.post('/auth/login', { username, password });
            const { access_token } = response.data;
            localStorage.setItem('token', access_token);
            return access_token;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },

    async logout() {
        localStorage.removeItem('token');
    },

    async getCurrentUser() {
        try {
            const response = await api.get('/auth/me');
            return response.data;
        } catch (error) {
            console.error('Error fetching current user:', error);
            throw error;
        }
    }
};