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

// Listen for login state changes across tabs and update token in memory if needed
window.addEventListener('storage', (event: StorageEvent) => {
  if (event.key === 'qvai_token') {
    // Optionally, trigger a global state update or reload user info here
    // For example, you could dispatch a custom event or use a state management library
    // window.dispatchEvent(new Event('qvai_auth_sync'));
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