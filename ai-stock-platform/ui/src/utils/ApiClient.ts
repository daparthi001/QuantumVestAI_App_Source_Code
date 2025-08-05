export const AUTH_STORAGE_KEYS = {
  TOKEN: 'qvai_token',
  USER: 'qvai_user',
  LAST_ACTIVITY: 'qvai_last_activity'
};

/**
 * Get token from localStorage for API requests
 * This function is called on every request to ensure we always use the most up-to-date token
 */
const getAuthToken = (): string | null => {
  return localStorage.getItem('qvai_token');
};

/**
 * Add authorization header if token exists
 */
const addAuthHeader = (headers: Record<string, string> = {}): Record<string, string> => {
  const token = getAuthToken();
  if (token) {
    return {
      ...headers,
      'Authorization': `Bearer ${token}`
    };
  }
  return headers;
};

// Ensure all existing users in localStorage are set to premium on load
try {
  const userStr = localStorage.getItem(AUTH_STORAGE_KEYS.USER);
  if (userStr) {
    const user = JSON.parse(userStr);
    if (user && user.role !== 'premium') {
      user.role = 'premium';
      localStorage.setItem(AUTH_STORAGE_KEYS.USER, JSON.stringify(user));
    }
  }
} catch (e) {
  // Ignore parse errors
}

// Listen for login state changes across tabs and update user role to premium if needed
window.addEventListener('storage', (event: StorageEvent) => {
  if (event.key === AUTH_STORAGE_KEYS.USER && event.newValue) {
    try {
      const user = JSON.parse(event.newValue);
      if (user && user.role !== 'premium') {
        user.role = 'premium';
        localStorage.setItem(AUTH_STORAGE_KEYS.USER, JSON.stringify(user));
      }
    } catch (e) {
      // Ignore parse errors
    }
  }
});

/**
 * Update last activity timestamp to manage session timeouts
 */
const updateLastActivity = (): void => {
  localStorage.setItem(AUTH_STORAGE_KEYS.LAST_ACTIVITY, Date.now().toString());
};

/**
 * API request with authentication
 * Uses the current token from localStorage and updates activity timestamp
 */
export const authenticatedRequest = async (
  url: string, 
  method: string = 'GET', 
  data?: any, 
  customHeaders?: Record<string, string>
) => {
  // Update last activity timestamp
  updateLastActivity();
  
  // Get current headers with auth token
  const headers = {
    'Content-Type': 'application/json',
    ...addAuthHeader(customHeaders)
  };

  // ...existing code...
};