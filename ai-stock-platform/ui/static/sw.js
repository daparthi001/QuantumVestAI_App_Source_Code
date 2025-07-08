/**
 * QuantumVestAI Service Worker
 * Offline support and caching for enhanced performance
 * Updated: 2025-01-09
 * Author: AI Enhancement System
 */

const CACHE_NAME = 'quantumvestai-v1.0.0';
const RUNTIME_CACHE = 'runtime-cache-v1';

// Critical resources to cache immediately
const PRECACHE_RESOURCES = [
  '/',
  '/login',
  '/register',
  '/static/css/quantum-enhancements.css',
  '/static/css/bootstrap.min.css',
  '/static/js/quantum-enhancements.js',
  '/static/js/quantum-i18n.js',
  '/static/js/quantum-search.js',
  '/static/js/bootstrap.bundle.min.js',
  '/static/manifest.json'
];

// Resources that can be cached at runtime
const RUNTIME_CACHE_PATTERNS = [
  /^https:\/\/fonts\.googleapis\.com\//,
  /^https:\/\/fonts\.gstatic\.com\//,
  /^https:\/\/cdn\.jsdelivr\.net\//,
  /\/static\/.*\.(css|js|png|jpg|jpeg|svg|webp|gif|ico)$/,
  /\/api\/.*$/
];

// Resources that should always be fetched fresh
const NETWORK_FIRST_PATTERNS = [
  /\/api\/realtime\//,
  /\/api\/live\//,
  /\/api\/market\/current/,
  /\/api\/portfolio\/current/
];

// Install event - precache critical resources
self.addEventListener('install', (event) => {
  console.log('QuantumVestAI Service Worker installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Precaching critical resources...');
        return cache.addAll(PRECACHE_RESOURCES);
      })
      .then(() => {
        console.log('QuantumVestAI Service Worker installed successfully');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker installation failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('QuantumVestAI Service Worker activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE) {
              console.log('Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('QuantumVestAI Service Worker activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - handle different caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip chrome-extension and other non-http(s) requests
  if (!url.protocol.startsWith('http')) {
    return;
  }
  
  event.respondWith(handleRequest(request));
});

async function handleRequest(request) {
  const url = new URL(request.url);
  
  try {
    // Network-first strategy for real-time data
    if (NETWORK_FIRST_PATTERNS.some(pattern => pattern.test(url.pathname))) {
      return await networkFirst(request);
    }
    
    // Cache-first strategy for static assets
    if (RUNTIME_CACHE_PATTERNS.some(pattern => pattern.test(url.href))) {
      return await cacheFirst(request);
    }
    
    // Stale-while-revalidate for HTML pages
    if (request.headers.get('accept')?.includes('text/html')) {
      return await staleWhileRevalidate(request);
    }
    
    // Default to network-first for everything else
    return await networkFirst(request);
    
  } catch (error) {
    console.error('Fetch error:', error);
    return await handleOfflineScenario(request);
  }
}

// Network-first strategy with cache fallback
async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful responses
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache:', request.url);
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    throw error;
  }
}

// Cache-first strategy with network fallback
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('Cache-first failed:', error);
    throw error;
  }
}

// Stale-while-revalidate strategy
async function staleWhileRevalidate(request) {
  const cache = await caches.open(RUNTIME_CACHE);
  const cachedResponse = await cache.match(request);
  
  // Start fetch in background
  const fetchPromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(() => {
    // Fetch failed, but we might have cache
    return null;
  });
  
  // Return cached version immediately if available
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Otherwise wait for network
  return await fetchPromise;
}

// Handle offline scenarios
async function handleOfflineScenario(request) {
  const url = new URL(request.url);
  
  // For HTML pages, show offline page
  if (request.headers.get('accept')?.includes('text/html')) {
    const offlinePageResponse = await caches.match('/offline.html');
    if (offlinePageResponse) {
      return offlinePageResponse;
    }
    
    // Fallback offline response
    return new Response(`
      <!DOCTYPE html>
      <html>
      <head>
          <title>Offline - QuantumVestAI</title>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <style>
              body {
                  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                  background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 50%, #0c0c0c 100%);
                  color: white;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  min-height: 100vh;
                  margin: 0;
                  text-align: center;
              }
              .offline-container {
                  max-width: 400px;
                  padding: 2rem;
              }
              .offline-icon {
                  font-size: 4rem;
                  margin-bottom: 1rem;
              }
              .offline-title {
                  font-size: 1.5rem;
                  margin-bottom: 1rem;
                  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                  -webkit-background-clip: text;
                  -webkit-text-fill-color: transparent;
                  background-clip: text;
              }
              .offline-message {
                  margin-bottom: 2rem;
                  opacity: 0.8;
              }
              .retry-btn {
                  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                  color: white;
                  border: none;
                  padding: 0.75rem 1.5rem;
                  border-radius: 8px;
                  cursor: pointer;
                  font-weight: 600;
              }
          </style>
      </head>
      <body>
          <div class="offline-container">
              <div class="offline-icon">📡</div>
              <h1 class="offline-title">You're Offline</h1>
              <p class="offline-message">
                  QuantumVestAI requires an internet connection. Please check your connection and try again.
              </p>
              <button class="retry-btn" onclick="window.location.reload()">
                  Retry Connection
              </button>
          </div>
      </body>
      </html>
    `, {
      status: 200,
      headers: { 'Content-Type': 'text/html' }
    });
  }
  
  // For API requests, return cached data or error
  if (url.pathname.startsWith('/api/')) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return new Response(JSON.stringify({
      error: 'Offline',
      message: 'This data is not available offline',
      timestamp: new Date().toISOString()
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  // For static assets, try to find in cache
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Final fallback
  return new Response('Resource not available offline', {
    status: 503,
    headers: { 'Content-Type': 'text/plain' }
  });
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('Background sync triggered:', event.tag);
  
  if (event.tag === 'portfolio-sync') {
    event.waitUntil(syncPortfolioData());
  } else if (event.tag === 'user-preferences') {
    event.waitUntil(syncUserPreferences());
  }
});

async function syncPortfolioData() {
  try {
    // Sync any queued portfolio changes
    const pendingActions = await getStoredActions('portfolio-actions');
    
    for (const action of pendingActions) {
      await fetch('/api/portfolio/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(action)
      });
    }
    
    await clearStoredActions('portfolio-actions');
    console.log('Portfolio data synced successfully');
  } catch (error) {
    console.error('Portfolio sync failed:', error);
  }
}

async function syncUserPreferences() {
  try {
    // Sync user preferences
    const preferences = await getStoredActions('user-preferences');
    
    for (const pref of preferences) {
      await fetch('/api/user/preferences', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pref)
      });
    }
    
    await clearStoredActions('user-preferences');
    console.log('User preferences synced successfully');
  } catch (error) {
    console.error('Preferences sync failed:', error);
  }
}

// Push notifications
self.addEventListener('push', (event) => {
  console.log('Push notification received:', event);
  
  const options = {
    body: 'You have new market updates!',
    icon: '/static/img/icons/icon-192x192.png',
    badge: '/static/img/icons/badge-72x72.png',
    data: {
      url: '/'
    },
    actions: [
      {
        action: 'view',
        title: 'View Dashboard'
      },
      {
        action: 'dismiss',
        title: 'Dismiss'
      }
    ]
  };
  
  if (event.data) {
    try {
      const data = event.data.json();
      options.body = data.message || options.body;
      options.data = data;
    } catch (error) {
      console.error('Error parsing push data:', error);
    }
  }
  
  event.waitUntil(
    self.registration.showNotification('QuantumVestAI', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('Notification clicked:', event);
  
  event.notification.close();
  
  if (event.action === 'view') {
    const url = event.notification.data?.url || '/';
    event.waitUntil(
      clients.openWindow(url)
    );
  }
});

// Utility functions for IndexedDB operations
async function getStoredActions(storeName) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('QuantumVestAI', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const getRequest = store.getAll();
      
      getRequest.onsuccess = () => resolve(getRequest.result || []);
      getRequest.onerror = () => reject(getRequest.error);
    };
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(storeName)) {
        db.createObjectStore(storeName, { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

async function clearStoredActions(storeName) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('QuantumVestAI', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const clearRequest = store.clear();
      
      clearRequest.onsuccess = () => resolve();
      clearRequest.onerror = () => reject(clearRequest.error);
    };
  });
}

// Version update notification
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

console.log('QuantumVestAI Service Worker loaded successfully');