/**
 * Configuration Index
 * Created: 2025-01-08
 * Author: daparthi001
 */

export * from './constants';

// Export a default configuration object
export default {
    api: {
        baseUrl:
            (typeof import.meta !== 'undefined' && import.meta.env.VITE_API_URL) ||
            (typeof process !== 'undefined' ? process.env.REACT_APP_API_URL : undefined) ||
            'http://quantumvestai-dev-api:8000',
        timeout: 30000
    },
    cache: {
        ttl: 300000, // 5 minutes
        maxSize: 100
    },
    performance: {
        enableMonitoring: true,
        reportingInterval: 60000 // 1 minute
    }
};

