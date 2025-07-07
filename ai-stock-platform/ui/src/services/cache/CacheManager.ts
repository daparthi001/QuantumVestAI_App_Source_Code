/**
 * Cache Management Service
 * Created: 2025-05-19 05:06:36
 * Author: daparthi001
 */
import { LRUCache } from 'lru-cache';
import { RealTimeMonitor } from '../monitoring/RealTimeMonitor';

export class CacheManager {
    private static instance: CacheManager;
    private memoryCache: LRUCache<string, any>;
    private indexedDB: IDBDatabase | null = null;
    private monitor: RealTimeMonitor;

    private constructor() {
        this.memoryCache = new LRUCache({
            max: 500, // Maximum number of items
            maxSize: 5000, // Maximum cache size in bytes
            sizeCalculation: (value, key) => {
                return new Blob([JSON.stringify(value)]).size;
            },
            ttl: 1000 * 60 * 60, // 1 hour default TTL
        });

        this.monitor = RealTimeMonitor.getInstance();
        this.initializeIndexedDB();
    }

    static getInstance(): CacheManager {
        if (!CacheManager.instance) {
            CacheManager.instance = new CacheManager();
        }
        return CacheManager.instance;
    }

    private async initializeIndexedDB(): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('AppCache', 1);

            request.onerror = () => {
                console.error('Failed to open IndexedDB');
                reject(request.error);
            };

            request.onsuccess = () => {
                this.indexedDB = request.result;
                resolve();
            };

            request.onupgradeneeded = (event: IDBVersionChangeEvent) => {
                const db = (event.target as IDBOpenDBRequest).result;
                if (!db.objectStoreNames.contains('cache')) {
                    db.createObjectStore('cache', { keyPath: 'key' });
                }
            };
        });
    }

    async set(key: string, value: any, options: {
        ttl?: number;
        persistent?: boolean;
        priority?: 'high' | 'medium' | 'low';
    } = {}): Promise<void> {
        const cacheItem = {
            key,
            value,
            timestamp: Date.now(),
            expiry: options.ttl ? Date.now() + options.ttl : undefined,
            priority: options.priority || 'medium'
        };

        // Set in memory cache
        this.memoryCache.set(key, cacheItem);

        // Set in IndexedDB if persistent
        if (options.persistent && this.indexedDB) {
            const transaction = this.indexedDB.transaction(['cache'], 'readwrite');
            const store = transaction.objectStore('cache');
            await store.put(cacheItem);
        }

        // Monitor cache usage
        this.monitor.trackMetric('cache_set', {
            key,
            size: new Blob([JSON.stringify(value)]).size,
            persistent: options.persistent
        });
    }

    async get(key: string): Promise<any | null> {
        // Try memory cache first
        const memoryItem = this.memoryCache.get(key);
        if (memoryItem) {
            if (this.isExpired(memoryItem)) {
                this.memoryCache.delete(key);
                return null;
            }
            return memoryItem.value;
        }

        // Try IndexedDB
        if (this.indexedDB) {
            const transaction = this.indexedDB.transaction(['cache'], 'readonly');
            const store = transaction.objectStore('cache');
            const request = store.get(key);

            return new Promise((resolve, reject) => {
                request.onsuccess = () => {
                    const item = request.result;
                    if (item && !this.isExpired(item)) {
                        // Cache in memory for future access
                        this.memoryCache.set(key, item);
                        resolve(item.value);
                    } else {
                        resolve(null);
                    }
                };
                request.onerror = () => reject(request.error);
            });
        }

        return null;
    }

    async invalidate(key: string): Promise<void> {
        this.memoryCache.delete(key);

        if (this.indexedDB) {
            const transaction = this.indexedDB.transaction(['cache'], 'readwrite');
            const store = transaction.objectStore('cache');
            await store.delete(key);
        }
    }

    async clear(): Promise<void> {
        this.memoryCache.clear();

        if (this.indexedDB) {
            const transaction = this.indexedDB.transaction(['cache'], 'readwrite');
            const store = transaction.objectStore('cache');
            await store.clear();
        }
    }

    private isExpired(item: any): boolean {
        return item.expiry && item.expiry < Date.now();
    }

    async getStats(): Promise<{
        memorySize: number;
        itemCount: number;
        hitRate: number;
    }> {
        return {
            memorySize: this.memoryCache.calculatedSize || 0,
            itemCount: this.memoryCache.size,
            hitRate: this.calculateHitRate()
        };
    }

    // Add missing methods for AutoOptimizer
    async pruneExpired(): Promise<void> {
        const keysToDelete: string[] = [];
        
        // Check memory cache
        for (const [key, item] of this.memoryCache.entries()) {
            if (this.isExpired(item)) {
                keysToDelete.push(key);
            }
        }
        
        // Remove expired items
        for (const key of keysToDelete) {
            this.memoryCache.delete(key);
        }
        
        // Also clean up IndexedDB if available
        if (this.indexedDB) {
            const transaction = this.indexedDB.transaction(['cache'], 'readwrite');
            const store = transaction.objectStore('cache');
            const request = store.openCursor();
            
            request.onsuccess = (event) => {
                const cursor = (event.target as IDBRequest).result;
                if (cursor) {
                    if (this.isExpired(cursor.value)) {
                        cursor.delete();
                    }
                    cursor.continue();
                }
            };
        }
    }

    cleanupEventListeners(): void {
        // Clean up any event listeners
        if (this.indexedDB) {
            this.indexedDB.close();
        }
    }

    preloadFrequentData(keys: string[]): Promise<void[]> {
        return Promise.all(keys.map(key => this.get(key)));
    }

    getComponentStats(componentName: string): Promise<any> {
        return this.get(`component_stats_${componentName}`);
    }

    async getAccessLogs(): Promise<any[]> {
        // Return cached access logs if available
        const logs = await this.get('access_logs');
        return logs || [];
    }

    async updateCacheSettings(settings: any): Promise<void> {
        await this.set('cache_settings', settings, { persistent: true });
    }

    private calculateHitRate(): number {
        // Simple hit rate calculation based on cache size vs theoretical max access
        const maxSize = this.memoryCache.max || 1000;
        const currentSize = this.memoryCache.size;
        return Math.min((currentSize / maxSize) * 100, 100);
    }
}