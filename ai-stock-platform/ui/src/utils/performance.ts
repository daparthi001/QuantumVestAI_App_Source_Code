/**
 * Performance Optimization Utilities
 * Created: 2025-05-19 04:58:03
 * Author: daparthi001
 */
import { useCallback, useRef, useEffect, useState, useMemo } from 'react';
import { debounce } from 'lodash';

// Custom hook for virtualized lists
export const useVirtualization = (itemCount: number, itemHeight: number) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [visibleRange, setVisibleRange] = useState({ start: 0, end: 0 });

    const updateVisibleRange = useCallback(() => {
        if (!containerRef.current) return;

        const { scrollTop, clientHeight } = containerRef.current;
        const start = Math.floor(scrollTop / itemHeight);
        const end = Math.min(
            Math.ceil((scrollTop + clientHeight) / itemHeight),
            itemCount
        );

        setVisibleRange({ start, end });
    }, [itemCount, itemHeight]);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        const debouncedUpdate = debounce(updateVisibleRange, 16);
        container.addEventListener('scroll', debouncedUpdate);

        return () => {
            container.removeEventListener('scroll', debouncedUpdate);
            debouncedUpdate.cancel();
        };
    }, [updateVisibleRange]);

    return { containerRef, visibleRange };
};

// Custom hook for memoized sorting
export const useSortedData = <T>(
    data: T[],
    sortKey: keyof T,
    sortDirection: 'asc' | 'desc'
) => {
    return useMemo(() => {
        return [...data].sort((a, b) => {
            const aValue = a[sortKey];
            const bValue = b[sortKey];
            return sortDirection === 'asc'
                ? aValue > bValue ? 1 : -1
                : aValue < bValue ? 1 : -1;
        });
    }, [data, sortKey, sortDirection]);
};

// Custom hook for data caching
export const useDataCache = <T>(key: string, ttl: number = 5000) => {
    const cache = useRef<Map<string, { data: T; timestamp: number }>>(new Map());

    const getData = useCallback((dataKey?: string): T | null => {
        const cacheKey = dataKey || key;
        const cached = cache.current.get(cacheKey);
        if (!cached) return null;

        const now = Date.now();
        if (now - cached.timestamp > ttl) {
            cache.current.delete(cacheKey);
            return null;
        }

        return cached.data;
    }, [key, ttl]);

    const setData = useCallback((key: string, data: T) => {
        cache.current.set(key, {
            data,
            timestamp: Date.now()
        });
    }, []);

    return { getData, setData };
};

// Performance monitoring
export const measurePerformance = (
    componentName: string,
    callback: () => void
) => {
    const start = performance.now();
    callback();
    const end = performance.now();
    const duration = end - start;

    if (duration > 16.67) { // Longer than one frame (60 fps)
        console.warn(
            `Performance warning: ${componentName} took ${duration.toFixed(2)}ms to render`
        );
    }
};

// Intersection Observer hook for lazy loading
export const useLazyLoad = (
    callback: () => void,
    options: IntersectionObserverInit = {}
) => {
    const targetRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(([entry]) => {
            if (entry.isIntersecting) {
                callback();
            }
        }, options);

        if (targetRef.current) {
            observer.observe(targetRef.current);
        }

        return () => {
            if (targetRef.current) {
                observer.unobserve(targetRef.current);
            }
        };
    }, [callback, options]);

    return targetRef;
};