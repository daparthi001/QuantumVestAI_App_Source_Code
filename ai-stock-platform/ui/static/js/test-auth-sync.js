/**
 * Test script for cross-tab authentication synchronization in QuantumVestAI
 * This file helps verify the auth-sync.js implementation
 * Updated: 2025-08-04
 */

// Function to test login synchronization
function testLoginSync() {
  console.log('=== Testing Login Sync ===');
  
  // Simulate login
  const token = 'test_token_' + Math.random().toString(36).substring(2);
  console.log('Setting token in localStorage:', token);
  
  // Set token in localStorage (should trigger storage event in other tabs)
  localStorage.setItem('qvai_token', token);
  
  // Verify cookies were updated
  setTimeout(() => {
    const cookieToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('qvai_token='));
      
    console.log('Cookie token after login:', cookieToken);
    
    if (cookieToken && cookieToken.split('=')[1] === token) {
      console.log('✓ SUCCESS: Cookie was properly updated with token');
    } else {
      console.log('✗ FAILURE: Cookie was not updated correctly');
    }
  }, 500);
}

// Function to test logout synchronization
function testLogoutSync() {
  console.log('=== Testing Logout Sync ===');
  
  // First make sure we have a token
  const token = localStorage.getItem('qvai_token') || 'test_token';
  localStorage.setItem('qvai_token', token);
  document.cookie = `qvai_token=${token}; path=/; samesite=lax`;
  document.cookie = `access_token=Bearer ${token}; path=/; samesite=lax`;
  
  console.log('Current localStorage token:', localStorage.getItem('qvai_token'));
  console.log('Current cookie:', document.cookie);
  
  // Simulate logout by removing token
  console.log('Removing token from localStorage (simulating logout)');
  localStorage.removeItem('qvai_token');
  
  // Verify cookies were removed
  setTimeout(() => {
    const cookieToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('qvai_token='));
      
    console.log('Cookie after logout:', document.cookie);
    
    if (!cookieToken) {
      console.log('✓ SUCCESS: Cookie was properly removed');
    } else {
      console.log('✗ FAILURE: Cookie was not removed correctly');
    }
  }, 500);
}

// Function to test redirect behavior
function testRedirectBehavior() {
  console.log('=== Testing Redirect Behavior ===');
  
  const isAuthenticated = !!localStorage.getItem('qvai_token');
  const currentPath = window.location.pathname;
  
  console.log('Current authentication state:', isAuthenticated ? 'Authenticated' : 'Not authenticated');
  console.log('Current path:', currentPath);
  
  if (isAuthenticated) {
    console.log('Testing redirect while authenticated on login page...');
    
    if (currentPath === '/login' || currentPath === '/auth/login') {
      console.log('On login page while authenticated - should redirect to dashboard');
      // Should redirect to dashboard automatically by auth-sync.js
    } else {
      console.log('Not on login page - no redirect expected');
    }
  } else {
    console.log('Testing redirect while not authenticated on protected page...');
    
    if (currentPath !== '/login' && currentPath !== '/auth/login' && 
        currentPath !== '/' && !currentPath.startsWith('/about')) {
      console.log('On protected page while not authenticated - should redirect to login');
      // Should redirect to login automatically by auth-sync.js
    } else {
      console.log('On public page - no redirect expected');
    }
  }
}

// Run tests from console
console.log('Auth sync test utilities loaded.');
console.log('Run tests individually with:');
console.log('- testLoginSync()');
console.log('- testLogoutSync()');
console.log('- testRedirectBehavior()');
console.log('Or run all tests with testAll()');

function testAll() {
  testLoginSync();
  setTimeout(testLogoutSync, 2000);
  setTimeout(testRedirectBehavior, 4000);
}

// Make functions available globally
window.testLoginSync = testLoginSync;
window.testLogoutSync = testLogoutSync;
window.testRedirectBehavior = testRedirectBehavior;
window.testAll = testAll;
