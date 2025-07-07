/**
 * Real-time Monitoring Service
 * Created: 2025-05-19 05:04:13
 * Author: daparthi001
 */
import { Subject, interval, merge } from 'rxjs';
import { switchMap, catchError } from 'rxjs/operators';
import { PerformanceMonitor } from './PerformanceMonitor';
import { hasMemorySupport } from '../../types/global';

export class RealTimeMonitor {
    private static instance: RealTimeMonitor;
    private metrics$ = new Subject<any>();
    private alerts$ = new Subject<any>();
    private _performanceMonitor: PerformanceMonitor;
    private subscribers: Set<(data: any) => void> = new Set();

    private constructor() {
        this._performanceMonitor = PerformanceMonitor.getInstance();
        this.initializeMonitoring();
    }

    static getInstance(): RealTimeMonitor {
        if (!RealTimeMonitor.instance) {
            RealTimeMonitor.instance = new RealTimeMonitor();
        }
        return RealTimeMonitor.instance;
    }

    private initializeMonitoring() {
        // Set up periodic metrics collection
        const metrics = interval(5000).pipe(
            switchMap(() => this.collectMetrics()),
            catchError((error) => {
                console.error('Error collecting metrics:', error);
                return [];
            })
        );

        // Set up alerts monitoring
        const alerts = interval(1000).pipe(
            switchMap(() => this.checkAlerts()),
            catchError((error) => {
                console.error('Error checking alerts:', error);
                return [];
            })
        );

        // Combine streams
        merge(metrics, alerts).subscribe((data) => {
            this.notifySubscribers(data);
        });
    }

    private async collectMetrics() {
        const metrics = {
            timestamp: Date.now(),
            cpu: await this.getCPUUsage(),
            memory: await this.getMemoryUsage(),
            network: await this.getNetworkMetrics(),
            renderTimes: await this.getRenderTimes()
        };

        this.metrics$.next(metrics);
        return metrics;
    }

    private async checkAlerts() {
        const thresholds = {
            cpuUsage: 80,
            memoryUsage: 90,
            responseTime: 1000
        };

        const metrics = await this.collectMetrics();
        const alerts = [];

        if (metrics.cpu > thresholds.cpuUsage) {
            alerts.push({
                type: 'cpu',
                level: 'warning',
                message: `High CPU usage: ${metrics.cpu}%`
            });
        }

        if (metrics.memory > thresholds.memoryUsage) {
            alerts.push({
                type: 'memory',
                level: 'warning',
                message: `High memory usage: ${metrics.memory}%`
            });
        }

        if (alerts.length > 0) {
            this.alerts$.next(alerts);
        }

        return alerts;
    }

    subscribe(callback: (data: any) => void) {
        this.subscribers.add(callback);
        return () => this.subscribers.delete(callback);
    }

    private notifySubscribers(data: any) {
        this.subscribers.forEach(callback => callback(data));
    }

    // Performance metrics collection methods
    private async getCPUUsage(): Promise<number> {
        // Implementation would depend on browser APIs
        return performance.now() % 100; // Dummy implementation
    }

    private async getMemoryUsage(): Promise<number> {
        if (hasMemorySupport(performance)) {
            return (performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit) * 100;
        }
        return 0;
    }

    private async getNetworkMetrics() {
        if (performance.getEntriesByType) {
            const resources = performance.getEntriesByType('resource');
            return {
                count: resources.length,
                totalDuration: resources.reduce((acc, r) => acc + r.duration, 0)
            };
        }
        return { count: 0, totalDuration: 0 };
    }

    private async getRenderTimes() {
        const entries = performance.getEntriesByType('measure');
        return entries.filter(entry => entry.name.startsWith('render_'));
    }

    // Add missing trackMetric method
    trackMetric(name: string, value: number): void {
        const metricData = {
            name,
            value,
            timestamp: Date.now(),
            type: 'metric'
        };
        this.metrics$.next(metricData);
    }
}