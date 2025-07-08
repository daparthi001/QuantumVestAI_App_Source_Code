/**
 * QuantumVestAI Service Worker
 * Created: 2025-01-09
 * Author: AI Assistant for QuantumVestAI
 */

const CACHE_NAME = 'quantumvestai-v1.0.0';
const urlsToCache = [
    '/',
    '/static/css/bootstrap.min.css',
    '/static/css/quantum-enhancements.css',
    '/static/css/quantum-mobile-enhanced.css',
    '/static/css/styles.css',
    '/static/css/dark-mode.css',
    '/static/js/quantum-enhanced-charts.js',
    '/static/js/quantum-community.js',
    '/static/js/quantum-ai.js',
    '/static/js/quantum-pwa.js',
    '/static/images/icons/icon-192x192.png',
    '/static/images/icons/icon-512x512.png',
    '/dashboard',
    '/stocks',
    '/portfolio',
    '/ai-predictions',
    '/subscription/plans',
    '/education'
];

// Install event - cache resources
self.addEventListener('install', event => {
    console.log('[ServiceWorker] Install');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[ServiceWorker] Caching app shell');
                return cache.addAll(urlsToCache);
            })
            .catch(error => {
                console.error('[ServiceWorker] Cache failed:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('[ServiceWorker] Activate');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[ServiceWorker] Removing old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
    // Skip cross-origin requests and non-GET requests
    if (!event.request.url.startsWith(self.location.origin) || event.request.method !== 'GET') {
        return;
    }
    
    // Handle API requests differently
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            networkFirstStrategy(event.request)
        );
        return;
    }
    
    // Handle static assets and pages
    event.respondWith(
        cacheFirstStrategy(event.request)
    );
});

// Cache-first strategy for static assets
async function cacheFirstStrategy(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        
        // Cache successful responses
        if (networkResponse.status === 200) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('[ServiceWorker] Fetch failed:', error);
        
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            return caches.match('/offline.html');
        }
        
        throw error;
    }
}

// Network-first strategy for API requests
async function networkFirstStrategy(request) {
    try {
        const networkResponse = await fetch(request);
        
        // Cache successful API responses for short term
        if (networkResponse.status === 200) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
            
            // Set expiry for API cache (5 minutes)
            setTimeout(() => {
                cache.delete(request);
            }, 5 * 60 * 1000);
        }
        
        return networkResponse;
    } catch (error) {
        console.error('[ServiceWorker] Network failed, trying cache:', error);
        
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        throw error;
    }
}

// Handle push notifications
self.addEventListener('push', event => {
    console.log('[ServiceWorker] Push received');
    
    let notificationData = {
        title: 'QuantumVestAI',
        body: 'New update available',
        icon: '/static/images/icons/icon-192x192.png',
        badge: '/static/images/icons/badge-72x72.png',
        tag: 'quantum-vest-ai',
        renotify: true
    };
    
    if (event.data) {
        try {
            const data = event.data.json();
            notificationData = { ...notificationData, ...data };
        } catch (e) {
            notificationData.body = event.data.text();
        }
    }
    
    const options = {
        body: notificationData.body,
        icon: notificationData.icon,
        badge: notificationData.badge,
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: notificationData.tag || '1',
            url: notificationData.url || '/'
        },
        actions: [
            {
                action: 'explore',
                title: 'View Details',
                icon: '/static/images/icons/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/images/icons/xmark.png'
            }
        ],
        requireInteraction: notificationData.requireInteraction || false
    };
    
    event.waitUntil(
        self.registration.showNotification(notificationData.title, options)
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
    console.log('[ServiceWorker] Notification click received');
    
    event.notification.close();
    
    if (event.action === 'close') {
        return;
    }
    
    const urlToOpen = event.notification.data?.url || '/dashboard';
    
    event.waitUntil(
        clients.matchAll({
            type: 'window',
            includeUncontrolled: true
        }).then(clientList => {
            // Check if there's already a window/tab open with the target URL
            for (const client of clientList) {
                if (client.url === urlToOpen && 'focus' in client) {
                    return client.focus();
                }
            }
            
            // If no window/tab is open, open a new one
            if (clients.openWindow) {
                return clients.openWindow(urlToOpen);
            }
        })
    );
});

// Handle notification close
self.addEventListener('notificationclose', event => {
    console.log('[ServiceWorker] Notification closed:', event.notification.tag);
    
    // Track notification close analytics
    if (self.registration.sync) {
        event.waitUntil(
            self.registration.sync.register('notification-close')
        );
    }
});

// Handle background sync
self.addEventListener('sync', event => {
    console.log('[ServiceWorker] Background sync:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    } else if (event.tag === 'notification-close') {
        event.waitUntil(trackNotificationClose());
    }
});

// Background sync for offline data
async function doBackgroundSync() {
    try {
        // Get offline data from IndexedDB or localStorage
        const offlineData = await getOfflineData();
        
        if (offlineData && offlineData.length > 0) {
            // Send offline data to server
            await fetch('/api/sync/offline-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(offlineData)
            });
            
            // Clear offline data after successful sync
            await clearOfflineData();
        }
    } catch (error) {
        console.error('[ServiceWorker] Background sync failed:', error);
    }
}

// Track notification close for analytics
async function trackNotificationClose() {
    try {
        await fetch('/api/analytics/notification-close', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                timestamp: Date.now(),
                type: 'notification_close'
            })
        });
    } catch (error) {
        console.error('[ServiceWorker] Analytics tracking failed:', error);
    }
}

// Helper functions for offline data management
async function getOfflineData() {
    // In a real implementation, this would read from IndexedDB
    // For now, return empty array
    return [];
}

async function clearOfflineData() {
    // In a real implementation, this would clear IndexedDB
    // For now, do nothing
}

// Handle messages from main thread
self.addEventListener('message', event => {
    console.log('[ServiceWorker] Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({ version: CACHE_NAME });
    }
});

// Periodic background sync (if supported)
if ('periodicsync' in self.registration) {
    self.addEventListener('periodicsync', event => {
        if (event.tag === 'update-stocks') {
            event.waitUntil(updateStocksInBackground());
        }
    });
}

async function updateStocksInBackground() {
    try {
        // Update cached stock data in background
        const response = await fetch('/api/stocks/trending');
        if (response.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put('/api/stocks/trending', response.clone());
        }
    } catch (error) {
        console.error('[ServiceWorker] Background stock update failed:', error);
    }
}

console.log('[ServiceWorker] Loaded successfully');