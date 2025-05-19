/**
 * API Service
 * Created: 2025-05-19 04:05:44
 * Author: daparthi001
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

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

export const stockService = {
    async getStockData(symbol: string) {
        const response = await api.get(`/stocks/${symbol}`);
        return response.data;
    },

    async getHistoricalPrices(symbol: string, startDate: string, endDate: string) {
        const response = await api.get(`/stocks/${symbol}/prices`, {
            params: { start_date: startDate, end_date: endDate }
        });
        return response.data;
    },

    async getTechnicalIndicators(symbol: string, indicators: string[]) {
        const response = await api.get(`/stocks/${symbol}/indicators`, {
            params: { indicators: indicators.join(',') }
        });
        return response.data;
    }
};

export const authService = {
    async login(username: string, password: string) {
        const response = await api.post('/auth/login', { username, password });
        const { access_token } = response.data;
        localStorage.setItem('token', access_token);
        return access_token;
    },

    async logout() {
        localStorage.removeItem('token');
    },

    async getCurrentUser() {
        const response = await api.get('/auth/me');
        return response.data;
    }
};