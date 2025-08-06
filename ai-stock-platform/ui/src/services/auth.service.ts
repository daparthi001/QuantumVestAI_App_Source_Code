/**
 * Authentication Service
 * Updated: 2025-06-19 18:00:37
 * Author: daparthi001
 */
import axios from 'axios';
import { BehaviorSubject } from 'rxjs';
import { API_BASE_URL } from '../config/constants';

// Define types
export interface User {
  username: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
}

export interface AuthResponse {
  status: string;
  message: string;
  data: {
    access_token: string;
    refresh_token?: string;
    token_type: string;
  };
}

export interface UserResponse {
  status: string;
  message: string;
  data: User;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface RegisterResponse {
  status: string;
  message: string;
  data: {
    username: string;
    email: string;
    full_name?: string;
  };
}

class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  private tokenSubject = new BehaviorSubject<string | null>(
    localStorage.getItem('qvai_token')
  );
  private refreshTokenKey = 'qvai_refresh_token';

  public currentUser = this.currentUserSubject.asObservable();
  public token = this.tokenSubject.asObservable();

  constructor() {
    // Check if we have a token and try to get user info
    if (this.getToken()) {
      this.fetchCurrentUser().catch(() => {
        // Token invalid, clear it
        this.logout();
      });
    }

    // Setup axios interceptors for auth
    axios.interceptors.request.use(async (config) => {
      const token = this.getToken();
      if (token) {
        config.headers = config.headers || {};
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      return config;
    });

    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response && error.response.status === 401) {
          try {
            const newToken = await this.refreshToken();
            error.config.headers['Authorization'] = `Bearer ${newToken}`;
            return axios(error.config);
          } catch (refreshError) {
            this.logout();
            return Promise.reject(refreshError);
          }
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Login to the application
   * @param username User's username
   * @param password User's password
   * @returns Promise with auth response
   */
  async login(username: string, password: string): Promise<AuthResponse> {
    // Create form data for login request
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await axios.post<AuthResponse>(
        `${API_BASE_URL}/api/v1/auth/login`, 
        formData,
        { 
          headers: { 
            'Content-Type': 'application/x-www-form-urlencoded' 
          }
        }
      );

      if (response.data.status === 'success' && response.data.data.access_token) {
        const token = response.data.data.access_token;
        const refreshToken = response.data.data.refresh_token;

        // Store token in local storage - this triggers storage event for cross-tab sync
        localStorage.setItem('qvai_token', token);
        if (refreshToken) {
          localStorage.setItem(this.refreshTokenKey, refreshToken);
        }

        // Persist token in cookies so server-rendered pages stay authenticated
        document.cookie = `qvai_token=${token}; path=/; samesite=lax`;
        document.cookie = `access_token=Bearer ${token}; path=/; samesite=lax`;

        // Update token subject
        this.tokenSubject.next(token);

        // Get user information
        await this.fetchCurrentUser();
        
        // Trigger auth event for cross-tab synchronization
        if (typeof window !== 'undefined' && window.dispatchEvent) {
          const authEvent = new CustomEvent('qvai_auth_event', {
            detail: { action: 'login', token: token }
          });
          window.dispatchEvent(authEvent);
        }
      }

      return response.data;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  /**
   * Register a new user
   * @param registerData User registration data
   * @returns Promise with registration response
   */
  async register(registerData: RegisterRequest): Promise<RegisterResponse> {
    try {
      const response = await axios.post<RegisterResponse>(
        `${API_BASE_URL}/api/v1/auth/register`, 
        registerData
      );
      
      return response.data;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  /**
   * Fetch current user information
   * @returns Promise with user data
   */
  async fetchCurrentUser(): Promise<User> {
    try {
        const token = this.getToken();
        if (!token) {
            throw new Error('No authentication token found');
        }

        const response = await axios.get<UserResponse>(
            `${API_BASE_URL}/api/v1/auth/me`, 
            {
                headers: { 
                    Authorization: `Bearer ${token}` 
                }
            }
        );

        if (response.data.status === 'success' && response.data.data) {
            const user = response.data.data;
            if (!user.role) {
                throw new Error('User role is missing');
            }
            this.currentUserSubject.next(user);
            return user;
        } else {
            throw new Error('Failed to fetch user data');
        }
    } catch (error) {
        console.error('Error fetching user data:', error);
        throw error;
    }
  }

  /**
   * Logout the current user
   */
  logout(): void {
    // Clear token from storage
    localStorage.removeItem('qvai_token');
    localStorage.removeItem(this.refreshTokenKey);

    // Remove authentication cookies
    document.cookie = 'qvai_token=; Max-Age=0; path=/';
    document.cookie = 'access_token=; Max-Age=0; path=/';
    document.cookie = 'user_info=; Max-Age=0; path=/';

    // Clear current user and token from subjects
    this.currentUserSubject.next(null);
    this.tokenSubject.next(null);
    
    // Trigger auth event for cross-tab synchronization
    if (typeof window !== 'undefined' && window.dispatchEvent) {
      const authEvent = new CustomEvent('qvai_auth_event', {
        detail: { action: 'logout' }
      });
      window.dispatchEvent(authEvent);
    }
  }

  /**
   * Get the current authentication token
   * @returns Current token or null
   */
  getToken(): string | null {
    return localStorage.getItem('qvai_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.refreshTokenKey);
  }

  /**
   * Check if user is authenticated
   * @returns True if authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  /**
   * Get current user value
   * @returns Current user or null
   */
  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  /**
   * Request password reset
   * @param email User's email
   * @returns Promise with response
   */
  async requestPasswordReset(email: string): Promise<any> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/auth/password-reset/request`,
        { email }
      );
      return response.data;
    } catch (error) {
      console.error('Password reset request failed:', error);
      throw error;
    }
  }

  /**
   * Reset password with token
   * @param token Reset token
   * @param newPassword New password
   * @returns Promise with response
   */
  async resetPassword(token: string, newPassword: string): Promise<any> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/auth/password-reset/confirm`,
        { token, new_password: newPassword }
      );
      return response.data;
    } catch (error) {
      console.error('Password reset failed:', error);
      throw error;
    }
  }

  /**
   * Refresh the authentication token
   * @returns Promise with new token
   */
  async refreshToken(): Promise<string> {
    try {
      const refreshToken = this.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      const response = await axios.post<AuthResponse>(
        `${API_BASE_URL}/api/v1/auth/refresh`,
        { refresh_token: refreshToken }
      );

      if (response.data.status === 'success' && response.data.data.access_token) {
        const newToken = response.data.data.access_token;

        // Update token in localStorage and cookies
        localStorage.setItem('qvai_token', newToken);
        document.cookie = `qvai_token=${newToken}; path=/; samesite=lax`;
        document.cookie = `access_token=Bearer ${newToken}; path=/; samesite=lax`;

        // Update token subject
        this.tokenSubject.next(newToken);

        return newToken;
      } else {
        throw new Error('Failed to refresh token');
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      throw error;
    }
  }

  /**
   * Intercept API calls to refresh token if expired
   * @param request Original request
   * @returns Modified request with refreshed token
   */
  async interceptRequest(request: any): Promise<any> {
    try {
      const token = this.getToken();
      if (!token) {
        throw new Error('No authentication token found');
      }

      const isTokenExpired = this.checkTokenExpiration(token); // Implement this method
      if (isTokenExpired) {
        const newToken = await this.refreshToken();
        request.headers.Authorization = `Bearer ${newToken}`;
      } else {
        request.headers.Authorization = `Bearer ${token}`;
      }

      return request;
    } catch (error) {
      console.error('Request interception failed:', error);
      throw error;
    }
  }

  private checkTokenExpiration(token: string): boolean {
    // Decode JWT and check expiration (implement decoding logic)
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  }
}

// Create singleton instance
const authService = new AuthService();

export default authService;