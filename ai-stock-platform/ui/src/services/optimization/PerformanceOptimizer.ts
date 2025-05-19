/**
 * Performance Optimizer Service
 * Created: 2025-05-19 05:05:29
 * Author: daparthi001
 */
import { debounce, throttle } from 'lodash';
import { RealTimeMonitor } from '../monitoring/RealTimeMonitor';

export class PerformanceOptimizer {
    private static instance: PerformanceOptimizer;
    private monitor: RealTimeMonitor;
    private optimizations: Map<string, boolean> = new Map();

    private constructor() {
        this.monitor = RealTimeMonitor.getInstance();
        this.initializeOptimizations();
    }

    static getInstance(): PerformanceOptimizer {
        if (!PerformanceOptimizer.instance) {
            PerformanceOptimizer.instance = new PerformanceOptimizer();
        }
        return PerformanceOptimizer.instance;
    }

    private initializeOptimizations() {
        // Initialize default optimization settings
        this.optimizations.set('virtualScrolling', true);
        this.optimizations.set('lazyLoading', true);
        this.optimizations.set('memoization', true);
        this.optimizations.set('debouncing', true);
        this.optimizations.set('compression', true);
    }

    // Memory optimization
    optimizeMemory() {
        return {
            clearUnusedData: () => {
                // Clear unnecessary data from memory
                window.localStorage.removeItem('temp_cache');
                if (window.performance && window.performance.memory) {
                    // Force garbage collection if possible
                    window.performance.memory.usedJSHeapSize = 0;
                }
            },

            limitCacheSize: (maxSize: number) => {
                const currentCache = JSON.parse(localStorage.getItem('app_cache') || '{}');
                const totalSize = new Blob([JSON.stringify(currentCache)]).size;
                
                if (totalSize > maxSize) {
                    // Remove oldest entries until under maxSize
                    const entries = Object.entries(currentCache);
                    entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
                    
                    while (entries.length && totalSize > maxSize) {
                        entries.shift();
                    }

                    localStorage.setItem('app_cache', JSON.stringify(Object.fromEntries(entries)));
                }
            }
        };
    }

    // Network optimization
    optimizeNetwork() {
        return {
            debounceRequests: debounce((fn: Function) => fn(), 300),
            
            throttleRequests: throttle((fn: Function) => fn(), 1000),
            
            batchRequests: async <T>(
                requests: Promise<T>[],
                batchSize: number = 5
            ): Promise<T[]> => {
                const results: T[] = [];
                for (let i = 0; i < requests.length; i += batchSize) {
                    const batch = requests.slice(i, i + batchSize);
                    const batchResults = await Promise.all(batch);
                    results.push(...batchResults);
                }
                return results;
            }
        };
    }

    // Rendering optimization
    optimizeRendering() {
        return {
            shouldComponentUpdate: (
                prevProps: any,
                nextProps: any,
                propsToCheck: string[]
            ): boolean => {
                return propsToCheck.some(
                    prop => prevProps[prop] !== nextProps[prop]
                );
            },

            memoizeComponent: <T extends Function>(
                component: T,
                dependencies: any[]
            ): T => {
                return React.memo(component, (prev, next) => {
                    return dependencies.every(
                        dep => prev[dep] === next[dep]
                    );
                }) as unknown as T;
            }
        };
    }

    // Data optimization
    optimizeData() {
        return {
            compressData: (data: any): string => {
                return LZString.compress(JSON.stringify(data));
            },

            decompressData: (compressed: string): any => {
                return JSON.parse(LZString.decompress(compressed));
            },

            cacheData: (key: string, data: any, ttl: number = 3600000) => {
                const cache = {
                    data,
                    timestamp: Date.now(),
                    expiry: Date.now() + ttl
                };
                localStorage.setItem(key, JSON.stringify(cache));
            }
        };
    }
}