/**
 * Configuration Index
 * Created: 2025-01-20
 * Author: daparthi001
 */

// Re-export all constants
export * from "./constants";

// Default configuration
export default {
  api: {
    baseUrl: process.env.REACT_APP_API_URL || "https://dev.quantumvestai.com",
    timeout: 30000,
  },
  features: {
    advancedAnalytics: true,
    aiAssistant: true,
    darkMode: true,
    realTimeData: true,
  },
};
