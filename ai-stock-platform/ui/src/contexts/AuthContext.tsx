/**
 * Auth Context
 * Created: 2025-06-19 17:56:46
 * Author: daparthi001
 */
import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import authService, { User } from '../services/auth.service';

// Define context interface
interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

// Create context with default values
const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => {},
  logout: () => {},
});

// Hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Props interface for the provider
interface AuthProviderProps {
  children: ReactNode;
}

// Auth Provider component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // Storage keys
  const TOKEN_KEY = 'qvai_token';
  const USER_KEY = 'qvai_user';
  const AUTH_EVENT = 'qvai_auth_change';

  // Initialize state from localStorage
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem(TOKEN_KEY);
  });
  
  const [user, setUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem(USER_KEY);
    return savedUser ? JSON.parse(savedUser) : null;
  });

  // Compute authentication status
  const isAuthenticated = !!token && !!user;
  const [isLoading, setIsLoading] = useState(true);

  // Handle login across tabs
  useEffect(() => {
    // Listen for storage events to sync state across tabs
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === TOKEN_KEY) {
        // Token has changed in another tab
        const newToken = event.newValue;
        setToken(newToken);
      } else if (event.key === USER_KEY) {
        // User has changed in another tab
        const newUser = event.newValue ? JSON.parse(event.newValue) : null;
        setUser(newUser);
      }
    };

    // Add event listeners
    window.addEventListener('storage', handleStorageChange);

    // Cleanup
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  // Rehydrate auth state on mount
  useEffect(() => {
    if (token && !user) {
      authService
        .fetchCurrentUser()
        .then((u) => {
          setUser(u);
          localStorage.setItem(USER_KEY, JSON.stringify(u));
        })
        .catch(() => {
          authService.logout();
          setToken(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  // Login function
  const login = async (username: string, password: string): Promise<void> => {
    try {
      await authService.login(username, password);
      const userData = authService.getCurrentUser();
      setUser(userData);
      
      // Update localStorage
      localStorage.setItem(TOKEN_KEY, authService.getToken()!);
      localStorage.setItem(USER_KEY, JSON.stringify(userData));
      
      // Dispatch event for cross-tab communication
      window.dispatchEvent(new Event(AUTH_EVENT));

      // Redirect to settings after successful login
      navigate('/settings', { replace: true });
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  // Logout function
  const logout = (): void => {
    authService.logout();
    setUser(null);
    
    // Clear localStorage
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    
    // Dispatch event for cross-tab communication
    window.dispatchEvent(new Event(AUTH_EVENT));

    navigate('/login');
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};