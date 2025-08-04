# Cross-Tab Authentication Synchronization in QuantumVestAI

## Overview

This document explains how cross-tab authentication synchronization is implemented in the QuantumVestAI application. This feature ensures that when a user logs in or out in one tab, the authentication state is synchronized across all open tabs, providing a seamless authentication experience.

## Implementation

### Files Modified

1. **`/static/js/auth-sync.js`** - Main script that handles cross-tab synchronization
2. **`/templates/base.html`** - Added auth-sync.js script
3. **`/static/js/auth.js`** - Updated to work with auth-sync.js
4. **`/src/services/auth.service.ts`** - Updated to dispatch auth events
5. **`/static/js/register.js`** - Updated to handle token synchronization

### How It Works

#### 1. Event-Based Synchronization

The system uses two mechanisms to synchronize authentication state:

- **Storage Events**: The `storage` event is fired when localStorage changes in other tabs
- **Custom Events**: Custom `qvai_auth_event` events for same-tab communication

#### 2. Token Management

All authentication tokens are now stored consistently:

- **`qvai_token`** in localStorage - Main token storage
- **`qvai_token`** and **`access_token`** cookies - For server-side authentication

#### 3. Login/Logout Flow

When a user logs in:
1. Token is stored in localStorage and cookies
2. Custom auth event is dispatched for current tab
3. Storage event triggers auth check in other tabs

When a user logs out:
1. Token is removed from localStorage and cookies
2. Custom auth event is dispatched for current tab
3. Storage event triggers auth check in other tabs

#### 4. Automatic Redirects

Based on authentication state:
- Logged-out users on protected pages are redirected to login
- Logged-in users on login/register pages are redirected to dashboard

### Testing the Implementation

You can test the cross-tab authentication synchronization using these test pages:

1. **Auth Sync Test**: `/auth/test-auth-sync` - Tests various auth scenarios
2. **Login Test**: `/auth/test-login` - Tests login functionality

Steps to test:
1. Open multiple tabs with the QuantumVestAI application
2. Log in or out in one tab
3. Observe that all tabs update to reflect the new authentication state

## Benefits

- Consistent user experience across multiple tabs
- Prevents authentication state confusion
- Automatic redirection based on auth state
- Enhanced security by ensuring complete logout

## Future Improvements

- Add session timeout handling
- Implement refresh token rotation
- Add visual indicators for auth state changes
