/**
 * Performance Tracking Hook
 * Created: 2025-05-19 05:01:47
 * Author: daparthi001
 */
import { useEffect, useRef } from 'react';
import { PerformanceMonitor } from '../services/monitoring/PerformanceMonitor';

export const usePerformanceTracking = (componentName: string) => {
    const monitor = PerformanceMonitor.getInstance();
    const renderStartRef = useRef<number>(0);
    const interactionStartRef = useRef<number>(0);

    useEffect(() => {
        const renderTime = performance.now() - renderStartRef.current;
        monitor.trackRenderTime(componentName, renderTime);
    });

    const trackInteraction = (interactionName: string) => {
        const duration = performance.now() - interactionStartRef.current;
        monitor.trackOrderOperation(interactionName, duration, true);
        interactionStartRef.current = performance.now();
    };

    const startInteraction = () => {
        interactionStartRef.current = performance.now();
    };

    // Start timing on mount
    useEffect(() => {
        renderStartRef.current = performance.now();
        return () => {
            // Track final render time on unmount
            const totalTime = performance.now() - renderStartRef.current;
            monitor.trackRenderTime(`${componentName}_total`, totalTime);
        };
    }, [componentName]);

    return {
        trackInteraction,
        startInteraction
    };
};