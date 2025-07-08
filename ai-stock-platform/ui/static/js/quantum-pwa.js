/**
 * Progressive Web App (PWA) Enhancement for QuantumVestAI
 * Created: 2025-01-09
 * Author: AI Assistant for QuantumVestAI
 */

class QuantumPWA {
    constructor() {
        this.isInstalled = false;
        this.deferredPrompt = null;
        this.notificationPermission = 'default';
        this.serviceWorkerRegistration = null;
        
        this.init();
    }

    init() {
        this.checkInstallation();
        this.setupServiceWorker();
        this.setupInstallPrompt();
        this.setupNotifications();
        this.setupOfflineHandling();
        this.setupAppShortcuts();
        this.addPWAStyles();
    }

    checkInstallation() {
        // Check if app is installed
        if (window.matchMedia('(display-mode: standalone)').matches) {
            this.isInstalled = true;
            this.hideInstallPrompt();
        }
        
        // Listen for app install
        window.addEventListener('appinstalled', () => {
            this.isInstalled = true;
            this.hideInstallPrompt();
            this.showNotification('QuantumVestAI installed successfully!', 'success');
        });
    }

    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/sw.js')
                .then(registration => {
                    this.serviceWorkerRegistration = registration;
                    console.log('ServiceWorker registered:', registration);
                    
                    // Check for updates
                    registration.addEventListener('updatefound', () => {
                        this.handleServiceWorkerUpdate(registration);
                    });
                })
                .catch(error => {
                    console.error('ServiceWorker registration failed:', error);
                });
        }
    }

    handleServiceWorkerUpdate(registration) {
        const newWorker = registration.installing;
        newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // New version available
                this.showUpdateAvailable();
            }
        });
    }

    showUpdateAvailable() {
        const updateBanner = document.createElement('div');
        updateBanner.className = 'update-banner';
        updateBanner.innerHTML = `
            <div class="update-content">
                <span class="update-text">🚀 New version available!</span>
                <button class="btn btn-sm btn-primary" onclick="quantumPWA.applyUpdate()">
                    Update Now
                </button>
                <button class="btn btn-sm btn-link" onclick="this.parentElement.parentElement.remove()">
                    Later
                </button>
            </div>
        `;
        
        document.body.insertBefore(updateBanner, document.body.firstChild);
    }

    applyUpdate() {
        if (this.serviceWorkerRegistration && this.serviceWorkerRegistration.waiting) {
            this.serviceWorkerRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
            window.location.reload();
        }
    }

    setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (event) => {
            event.preventDefault();
            this.deferredPrompt = event;
            this.showInstallPrompt();
        });
    }

    showInstallPrompt() {
        if (this.isInstalled) return;
        
        const installBanner = document.createElement('div');
        installBanner.className = 'install-banner';
        installBanner.innerHTML = `
            <div class="install-content">
                <div class="install-info">
                    <div class="install-icon">📱</div>
                    <div class="install-text">
                        <strong>Install QuantumVestAI</strong>
                        <span>Get faster access and offline features</span>
                    </div>
                </div>
                <div class="install-actions">
                    <button class="btn btn-primary btn-sm" onclick="quantumPWA.promptInstall()">
                        Install
                    </button>
                    <button class="btn btn-link btn-sm" onclick="quantumPWA.dismissInstall()">
                        Not now
                    </button>
                </div>
            </div>
        `;
        
        // Add to page if not already present
        if (!document.querySelector('.install-banner')) {
            document.body.appendChild(installBanner);
        }
    }

    promptInstall() {
        if (this.deferredPrompt) {
            this.deferredPrompt.prompt();
            this.deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                }
                this.deferredPrompt = null;
                this.hideInstallPrompt();
            });
        }
    }

    dismissInstall() {
        this.hideInstallPrompt();
        // Remember user dismissed (could store in localStorage)
        localStorage.setItem('installPromptDismissed', Date.now().toString());
    }

    hideInstallPrompt() {
        const installBanner = document.querySelector('.install-banner');
        if (installBanner) {
            installBanner.remove();
        }
    }

    setupNotifications() {
        if ('Notification' in window) {
            this.notificationPermission = Notification.permission;
            
            if (this.notificationPermission === 'default') {
                this.requestNotificationPermission();
            }
        }
    }

    async requestNotificationPermission() {
        try {
            const permission = await Notification.requestPermission();
            this.notificationPermission = permission;
            
            if (permission === 'granted') {
                this.showNotification('Notifications enabled! You\'ll receive important updates.', 'success');
                this.subscribeToWebPush();
            }
        } catch (error) {
            console.error('Notification permission request failed:', error);
        }
    }

    async subscribeToWebPush() {
        if (!this.serviceWorkerRegistration) return;
        
        try {
            const subscription = await this.serviceWorkerRegistration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(
                    'BPFk8yGf-DvDxQYX6KgGMd0jzYE9A3XPJ7CJ0Zqyqn8ZVm2fWZg3b-8HyC6a8E9Zv3Xj5n8F2kNYcVJT9b4R8'
                )
            });
            
            // Send subscription to server
            this.sendSubscriptionToServer(subscription);
        } catch (error) {
            console.error('Web push subscription failed:', error);
        }
    }

    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');
        
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    sendSubscriptionToServer(subscription) {
        // Send push subscription to server
        fetch('/api/notifications/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                subscription: subscription,
                userId: this.getCurrentUserId()
            })
        }).catch(error => {
            console.error('Failed to send subscription to server:', error);
        });
    }

    showNotification(message, type = 'info', options = {}) {
        // In-app notification
        const notification = document.createElement('div');
        notification.className = `pwa-notification pwa-notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">
                    ${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}
                </span>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
        
        // System notification if permission granted
        if (this.notificationPermission === 'granted' && options.system !== false) {
            new Notification('QuantumVestAI', {
                body: message,
                icon: '/static/images/icons/icon-192x192.png',
                badge: '/static/images/icons/badge-72x72.png',
                tag: 'quantum-vest-ai',
                renotify: true,
                ...options
            });
        }
    }

    setupOfflineHandling() {
        window.addEventListener('online', () => {
            this.showNotification('You\'re back online!', 'success');
            this.syncOfflineData();
        });
        
        window.addEventListener('offline', () => {
            this.showNotification('You\'re offline. Some features may be limited.', 'info');
        });
        
        // Check initial state
        if (!navigator.onLine) {
            this.showOfflineMode();
        }
    }

    showOfflineMode() {
        const offlineBanner = document.createElement('div');
        offlineBanner.className = 'offline-banner';
        offlineBanner.innerHTML = `
            <div class="offline-content">
                <span class="offline-icon">📡</span>
                <span class="offline-text">Offline Mode - Limited functionality available</span>
            </div>
        `;
        
        document.body.insertBefore(offlineBanner, document.body.firstChild);
    }

    syncOfflineData() {
        // Sync any offline data when connection restored
        const offlineData = localStorage.getItem('offlineData');
        if (offlineData) {
            try {
                const data = JSON.parse(offlineData);
                // Send offline data to server
                this.sendOfflineDataToServer(data);
                localStorage.removeItem('offlineData');
            } catch (error) {
                console.error('Failed to sync offline data:', error);
            }
        }
    }

    sendOfflineDataToServer(data) {
        fetch('/api/sync/offline-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        }).catch(error => {
            console.error('Failed to sync offline data:', error);
        });
    }

    setupAppShortcuts() {
        // Add keyboard shortcuts for PWA
        document.addEventListener('keydown', (event) => {
            if (event.ctrlKey || event.metaKey) {
                switch (event.key) {
                    case 'd':
                        event.preventDefault();
                        this.navigateTo('/dashboard');
                        break;
                    case 's':
                        event.preventDefault();
                        this.navigateTo('/stocks');
                        break;
                    case 'p':
                        event.preventDefault();
                        this.navigateTo('/portfolio');
                        break;
                    case 'a':
                        event.preventDefault();
                        this.navigateTo('/ai-predictions');
                        break;
                }
            }
        });
    }

    navigateTo(path) {
        if (window.location.pathname !== path) {
            window.location.href = path;
        }
    }

    addPWAStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* PWA Styles */
            .install-banner, .update-banner, .offline-banner {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 9999;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                animation: slideDown 0.3s ease-out;
            }
            
            .install-content, .update-content, .offline-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .install-info {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .install-icon {
                font-size: 24px;
            }
            
            .install-text {
                display: flex;
                flex-direction: column;
                gap: 2px;
            }
            
            .install-text strong {
                font-weight: 600;
            }
            
            .install-text span {
                font-size: 14px;
                opacity: 0.9;
            }
            
            .install-actions, .update-content {
                display: flex;
                gap: 8px;
                align-items: center;
            }
            
            .offline-content {
                justify-content: center;
                gap: 8px;
            }
            
            .offline-banner {
                background: linear-gradient(135deg, #ffa726 0%, #ff7043 100%);
            }
            
            .pwa-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                max-width: 400px;
                animation: slideInRight 0.3s ease-out;
            }
            
            .pwa-notification-success {
                border-left: 4px solid #28a745;
            }
            
            .pwa-notification-error {
                border-left: 4px solid #dc3545;
            }
            
            .pwa-notification-info {
                border-left: 4px solid #17a2b8;
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                padding: 16px;
                gap: 12px;
            }
            
            .notification-icon {
                font-size: 18px;
            }
            
            .notification-message {
                flex: 1;
                font-size: 14px;
                color: #333;
            }
            
            .notification-close {
                background: none;
                border: none;
                font-size: 18px;
                color: #999;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .notification-close:hover {
                color: #333;
            }
            
            @keyframes slideDown {
                from {
                    transform: translateY(-100%);
                }
                to {
                    transform: translateY(0);
                }
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            /* Mobile PWA optimizations */
            @media (max-width: 768px) {
                .install-content {
                    flex-direction: column;
                    gap: 12px;
                    text-align: center;
                }
                
                .install-info {
                    flex-direction: column;
                    gap: 8px;
                }
                
                .pwa-notification {
                    left: 20px;
                    right: 20px;
                    max-width: none;
                }
            }
            
            /* iOS PWA styles */
            @media (display-mode: standalone) {
                body {
                    padding-top: env(safe-area-inset-top);
                    padding-bottom: env(safe-area-inset-bottom);
                }
                
                .navbar {
                    padding-top: calc(8px + env(safe-area-inset-top));
                }
            }
        `;
        
        document.head.appendChild(style);
    }

    getCurrentUserId() {
        // Get current user ID (implement based on your auth system)
        return localStorage.getItem('userId') || 'anonymous';
    }

    // Stock price alerts integration
    createPriceAlert(symbol, targetPrice, condition) {
        const alert = {
            id: Date.now().toString(),
            symbol,
            targetPrice,
            condition,
            created: new Date().toISOString()
        };
        
        // Store alert
        const alerts = JSON.parse(localStorage.getItem('priceAlerts') || '[]');
        alerts.push(alert);
        localStorage.setItem('priceAlerts', JSON.stringify(alerts));
        
        this.showNotification(`Price alert created for ${symbol} at $${targetPrice}`, 'success');
        
        // Start monitoring (in real app, this would be server-side)
        this.monitorPriceAlert(alert);
        
        return alert;
    }

    monitorPriceAlert(alert) {
        // Simulate price monitoring
        setTimeout(() => {
            const shouldTrigger = Math.random() > 0.7; // 30% chance to trigger
            if (shouldTrigger) {
                this.triggerPriceAlert(alert);
            } else {
                this.monitorPriceAlert(alert); // Continue monitoring
            }
        }, 30000); // Check every 30 seconds (for demo)
    }

    triggerPriceAlert(alert) {
        const message = `🚨 ${alert.symbol} has reached your target price of $${alert.targetPrice}`;
        
        this.showNotification(message, 'success', {
            tag: `price-alert-${alert.id}`,
            requireInteraction: true,
            actions: [
                {
                    action: 'view',
                    title: 'View Stock'
                },
                {
                    action: 'dismiss',
                    title: 'Dismiss'
                }
            ]
        });
        
        // Remove triggered alert
        const alerts = JSON.parse(localStorage.getItem('priceAlerts') || '[]');
        const updatedAlerts = alerts.filter(a => a.id !== alert.id);
        localStorage.setItem('priceAlerts', JSON.stringify(updatedAlerts));
    }

    // Share stock analysis
    shareAnalysis(symbol, analysis) {
        if (navigator.share) {
            navigator.share({
                title: `${symbol} Stock Analysis - QuantumVestAI`,
                text: `Check out this AI-powered analysis for ${symbol}`,
                url: `${window.location.origin}/stocks/${symbol}`
            });
        } else {
            // Fallback to clipboard
            const shareText = `${symbol} Stock Analysis: ${analysis.summary} - Analyzed by QuantumVestAI ${window.location.origin}/stocks/${symbol}`;
            navigator.clipboard.writeText(shareText).then(() => {
                this.showNotification('Analysis link copied to clipboard!', 'success');
            });
        }
    }
}

// Initialize PWA features
const quantumPWA = new QuantumPWA();

// Service Worker for PWA
const serviceWorkerContent = `
// QuantumVestAI Service Worker
const CACHE_NAME = 'quantumvestai-v1.0.0';
const urlsToCache = [
    '/',
    '/static/css/quantum-design-system.css',
    '/static/css/quantum-mobile-enhanced.css',
    '/static/js/quantum-enhanced-charts.js',
    '/static/js/quantum-community.js',
    '/static/js/quantum-ai.js',
    '/static/images/icons/icon-192x192.png',
    '/static/images/icons/icon-512x512.png',
    '/dashboard',
    '/stocks',
    '/portfolio',
    '/ai-predictions'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
    );
});

// Handle push notifications
self.addEventListener('push', event => {
    const options = {
        body: event.data ? event.data.text() : 'New update from QuantumVestAI',
        icon: '/static/images/icons/icon-192x192.png',
        badge: '/static/images/icons/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: '1'
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
        ]
    };

    event.waitUntil(
        self.registration.showNotification('QuantumVestAI', options)
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();

    if (event.action === 'explore') {
        event.waitUntil(clients.openWindow('/dashboard'));
    }
});

self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});
`;

// Create service worker file if it doesn't exist
if ('serviceWorker' in navigator) {
    fetch('/static/js/sw.js').catch(() => {
        // Service worker doesn't exist, create it
        const blob = new Blob([serviceWorkerContent], { type: 'application/javascript' });
        const url = URL.createObjectURL(blob);
        navigator.serviceWorker.register(url);
    });
}

// Export for use in other modules
window.QuantumPWA = QuantumPWA;
window.quantumPWA = quantumPWA;