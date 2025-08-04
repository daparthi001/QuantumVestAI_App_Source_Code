/**
 * Cross-tab Authentication Synchronization for QuantumVestAI
 * Ensures login state is synced across multiple browser tabs
 * Updated: 2025-08-04
 * Author: GitHub Copilot
 */

(function() {
    // Constants
    const TOKEN_KEY = 'qvai_token';
    const AUTH_EVENT = 'qvai_auth_event';
    
    // Initialize the auth sync
    function initAuthSync() {
        console.log('Auth sync initialized');
        
        // Listen for storage events (when localStorage changes in another tab)
        window.addEventListener('storage', handleStorageEvent);
        
        // Create a custom event for auth changes in the current tab
        window.addEventListener(AUTH_EVENT, handleAuthEvent);
        
        // Initial check
        checkAuthState();
    }
    
    // Handle storage events (triggered when another tab modifies localStorage)
    function handleStorageEvent(event) {
        // Only respond to changes in the token
        if (event.key === TOKEN_KEY) {
            console.log('Auth state changed in another tab');
            checkAuthState();
        }
    }
    
    // Handle custom auth events within the same tab
    function handleAuthEvent(event) {
        console.log('Auth event received:', event.detail);
        checkAuthState();
    }
    
    // Check current auth state and respond accordingly
    function checkAuthState() {
        const token = localStorage.getItem(TOKEN_KEY);
        const isAuthenticated = !!token;
        
        // Check if the cookie token matches localStorage token
        const cookieToken = getTokenFromCookie(TOKEN_KEY);
        const cookieAuthToken = getTokenFromCookie('access_token')?.replace('Bearer ', '');
        
        // Get the current URL path
        const currentPath = window.location.pathname;
        
        // If we're logged out (no token in localStorage)
        if (!isAuthenticated) {
            console.log('Not authenticated, checking if we need to redirect');
            
            // If we have a cookie token but no localStorage token
            if (cookieToken || cookieAuthToken) {
                console.log('Cookie token exists but localStorage token is missing');
                // Cookie exists but localStorage doesn't - this could mean another tab logged out
                // Remove cookies to ensure consistent state
                document.cookie = `${TOKEN_KEY}=; Max-Age=0; path=/`;
                document.cookie = 'access_token=; Max-Age=0; path=/';
                document.cookie = 'user_info=; Max-Age=0; path=/';
            }
            
            // If we're on a protected page, redirect to login
            if (isProtectedPage(currentPath)) {
                console.log('On protected page while logged out, redirecting to login');
                redirectToLogin();
            }
        } 
        // If we're logged in (have token in localStorage)
        else {
            console.log('Authenticated, syncing cookies if needed');
            
            // If localStorage has a token but cookie doesn't, sync the cookie
            if (!cookieToken) {
                console.log('Syncing token to cookie');
                document.cookie = `${TOKEN_KEY}=${token}; path=/; samesite=lax`;
            }
            
            if (!cookieAuthToken) {
                console.log('Syncing auth token to cookie');
                document.cookie = `access_token=Bearer ${token}; path=/; samesite=lax`;
            }
            
            // If we're on the login or register page, redirect to dashboard
            if (isLoginPage(currentPath) || isRegisterPage(currentPath)) {
                console.log('On login/register page while logged in, redirecting to dashboard');
                window.location.href = '/dashboard';
            }
        }
    }
    
    // Helper: Check if current page is a protected page requiring authentication
    function isProtectedPage(path) {
        const publicPaths = ['/', '/login', '/auth/login', '/register', '/auth/register', 
                            '/about', '/contact', '/password-reset', '/terms', '/privacy'];
        
        // If path is in the public paths list, it's not protected
        if (publicPaths.some(p => path === p || path.startsWith(p + '/'))) {
            return false;
        }
        
        return true;
    }
    
    // Helper: Check if current page is the login page
    function isLoginPage(path) {
        return path === '/login' || path === '/auth/login';
    }
    
    // Helper: Check if current page is the registration page
    function isRegisterPage(path) {
        return path === '/register' || path === '/auth/register';
    }
    
    // Helper: Redirect to login page
    function redirectToLogin() {
        // Store current URL to redirect back after login
        const currentUrl = window.location.pathname + window.location.search;
        
        // Don't redirect if we're already on the login page
        if (isLoginPage(window.location.pathname)) {
            return;
        }
        
        // Redirect to login page with return URL
        window.location.href = `/auth/login?next=${encodeURIComponent(currentUrl)}`;
    }
    
    // Helper: Get token from cookie
    function getTokenFromCookie(name) {
        const match = document.cookie.match(new RegExp('(?:^|; )' + 
            name.replace(/([.$?*|{}()[\]\\/+^])/g, '\\$1') + '=([^;]*)'));
        return match ? decodeURIComponent(match[1]) : null;
    }
    
    // Expose a function to trigger auth state check from other scripts
    window.checkAuthSync = function() {
        const event = new CustomEvent(AUTH_EVENT, { 
            detail: { source: 'manual_check' } 
        });
        window.dispatchEvent(event);
    };
    
    // Enhance window.authUtils (if it exists)
    if (window.authUtils) {
        const originalSetToken = window.authUtils.setToken;
        const originalRemoveToken = window.authUtils.removeToken;
        
        // Override setToken to dispatch an event when token is set
        window.authUtils.setToken = function(token, remember = false) {
            originalSetToken.call(window.authUtils, token, remember);
            
            // Dispatch event for other scripts in this tab
            const event = new CustomEvent(AUTH_EVENT, {
                detail: { action: 'login', token: token }
            });
            window.dispatchEvent(event);
        };
        
        // Override removeToken to dispatch an event when token is removed
        window.authUtils.removeToken = function() {
            originalRemoveToken.call(window.authUtils);
            
            // Dispatch event for other scripts in this tab
            const event = new CustomEvent(AUTH_EVENT, {
                detail: { action: 'logout' }
            });
            window.dispatchEvent(event);
        };
    }
    
    // Initialize when the DOM is fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAuthSync);
    } else {
        initAuthSync();
    }
})();
