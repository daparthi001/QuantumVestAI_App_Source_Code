/**
 * Feature Provider Component
 * Created: 2025-06-19 18:06:43
 * Author: daparthi001
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import apiClient from '../services/api';
import { FEATURE_FLAGS } from '../config/constants';

// Feature flags interface
interface FeatureFlags {
  ADVANCED_ANALYTICS: boolean;
  AI_ASSISTANT: boolean;
  PORTFOLIO_OPTIMIZATION: boolean;
  SOCIAL_SENTIMENT: boolean;
  STRATEGY_BACKTESTING: boolean;
  DARK_MODE: boolean;
  REAL_TIME_DATA: boolean;
  PUSH_NOTIFICATIONS: boolean;
  [key: string]: boolean; // Allow dynamic feature flags
}

// Context type
interface FeatureContextType {
  features: FeatureFlags;
  isFeatureEnabled: (feature: keyof FeatureFlags | string) => boolean;
  loading: boolean;
}

// Create context with default values
const FeatureContext = createContext<FeatureContextType>({
  features: FEATURE_FLAGS,
  isFeatureEnabled: () => false,
  loading: true,
});

// Props interface
interface FeatureProviderProps {
  children: ReactNode;
}

export const FeatureProvider: React.FC<FeatureProviderProps> = ({ children }) => {
  const [features, setFeatures] = useState<FeatureFlags>(FEATURE_FLAGS);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Function to load feature flags from API
    const loadFeatureFlags = async () => {
      try {
        // Try to load feature flags from API
        const viteEnv: Record<string, string> = (typeof import.meta !== 'undefined' && import.meta.env) || {};
        const endpoint =
          viteEnv.VITE_FEATURE_FLAGS_ENDPOINT ||
          (typeof process !== 'undefined' ? process.env.REACT_APP_FEATURE_FLAGS_ENDPOINT : undefined) ||
          '/api/v1/feature-flags';
        const response = await apiClient.get(endpoint);
        
        if (response.data && response.data.data) {
          // Merge API flags with default flags
          setFeatures(prevFlags => ({
            ...prevFlags,
            ...response.data.data
          }));
        }
      } catch (error) {
        console.warn('Failed to load feature flags from API, using defaults', error);
      } finally {
        setLoading(false);
      }
    };

    loadFeatureFlags();
  }, []);

  // Check if a feature is enabled
  const isFeatureEnabled = (feature: keyof FeatureFlags | string): boolean => {
    return features[feature as keyof FeatureFlags] === true;
  };

  // Context value
  const value = {
    features,
    isFeatureEnabled,
    loading,
  };

  return (
    <FeatureContext.Provider value={value}>
      {children}
    </FeatureContext.Provider>
  );
};

// Hook for using the feature context
export const useFeatures = (): FeatureContextType => {
  return useContext(FeatureContext);
};