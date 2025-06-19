/**
 * API Service
 * Updated: 2025-06-19 04:23:15
 * Author: daparthi001
 */
import axios, { AxiosError, AxiosRequestConfig } from 'axios';

// Use environment variable or default to the relative path
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 15000, // Increased timeout for slower connections
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor for token
api.interceptors.request.use(
    (config: AxiosRequestConfig) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers = {
                ...config.headers,
                Authorization: `Bearer ${token}`
            };
        }
        return config;
    },
    (error) => {
        console.error('Request error:', error);
        return Promise.reject(error);
    }
);

// Add response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        // Log detailed error for debugging
        const requestUrl = error.config?.url;
        const requestMethod = error.config?.method;
        
        console.error(`API Error: ${requestMethod?.toUpperCase()} ${requestUrl}`);
        console.error('Status:', error.response?.status);
        console.error('Data:', error.response?.data);
        
        const status = error.response?.status;
        
        // Handle authentication errors
        if (status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login?session_expired=true';
            return Promise.reject(new Error('Your session has expired. Please log in again.'));
        }
        
        // Handle API service unavailable
        if (status === 503) {
            return Promise.reject(new Error('API service is currently unavailable. Please try again later.'));
        }
        
        // Handle rate limiting
        if (status === 429) {
            return Promise.reject(new Error('Too many requests. Please try again later.'));
        }
        
        // Return the original error
        return Promise.reject(error);
    }
);

// Authentication service
export const authService = {
    async login(username: string, password: string) {
        try {
            // Use URLSearchParams for form data (required by OAuth2)
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);
            
            const response = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });
            
            const { access_token } = response.data.data;
            localStorage.setItem('token', access_token);
            return access_token;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },
    
    async logout() {
        localStorage.removeItem('token');
        return Promise.resolve();
    },
    
    async getCurrentUser() {
        const response = await api.get('/auth/me');
        return response.data.data;
    },
    
    isAuthenticated() {
        return !!localStorage.getItem('token');
    }
};

// Other service exports...
export { api };