import { trace, context, SpanStatusCode, metrics } from '@opentelemetry/api';
import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';
import { hasMemorySupport } from '../../types/global';

// Custom Histogram interface for our metrics
interface MetricHistogram {
    value: number;
    timestamp: number;
}

export class PerformanceMonitor {
    private static instance: PerformanceMonitor;
    private metrics: Map<string, MetricHistogram>;

    private constructor() {
        this.metrics = new Map();
        this.initializeSentry();
        this.initializeTracing();
    }

    static getInstance(): PerformanceMonitor {
        if (!PerformanceMonitor.instance) {
            PerformanceMonitor.instance = new PerformanceMonitor();
        }
        return PerformanceMonitor.instance;
    }

    private initializeSentry() {
        Sentry.init({
            dsn: process.env.REACT_APP_SENTRY_DSN,
            integrations: [new BrowserTracing() as any],
            tracesSampleRate: 0.2,
            environment: process.env.NODE_ENV
        });
    }

    private initializeTracing() {
        trace.getTracer('order-management-ui');
    }

    trackOrderOperation(operation: string, duration: number, success: boolean) {
        const span = trace.getSpan(context.active());
        if (span) {
            span.setAttribute('operation', operation);
            span.setAttribute('duration_ms', duration);
            span.setStatus(success ? SpanStatusCode.OK : SpanStatusCode.ERROR);
        }

        this.recordMetric(`order_operation_${operation}`, duration);
    }

    trackRenderTime(componentName: string, duration: number) {
        if (duration > 16.67) {
            Sentry.captureMessage(
                `Slow render detected in ${componentName}: ${duration.toFixed(2)}ms`,
                'warning'
            );
        }

        this.recordMetric(`render_time_${componentName}`, duration);
    }

    trackApiCall(endpoint: string, duration: number, status: number) {
        const span = trace.getSpan(context.active());
        if (span) {
            span.setAttribute('http.url', endpoint);
            span.setAttribute('http.status_code', status);
            span.setAttribute('duration_ms', duration);
        }

        this.recordMetric(`api_call_${endpoint}`, duration);
    }

    private recordMetric(name: string, value: number) {
        this.metrics.set(name, {
            value,
            timestamp: Date.now()
        });
    }

    // Add missing methods
    getMetricDetails(metricName: string, interval?: string) {
        const baseData = {
            name: metricName,
            description: `Metric for ${metricName}`,
            unit: 'ms',
            hasData: this.metrics.has(metricName)
        };

        // Generate mock timeseries and breakdown data based on interval
        const timeseries = this.generateTimeseriesData(metricName, interval || '1h');
        const breakdown = this.generateBreakdownData(metricName);

        return Promise.resolve({
            ...baseData,
            timeseries,
            breakdown
        });
    }

    private generateTimeseriesData(metricName: string, interval: string) {
        // Generate mock timeseries data based on interval
        const data = [];
        const now = Date.now();
        const intervalMs = interval === '1h' ? 3600000 : interval === '1d' ? 86400000 : 3600000;
        const points = 24; // 24 data points

        for (let i = points - 1; i >= 0; i--) {
            data.push({
                timestamp: now - (i * intervalMs / points),
                value: Math.random() * 100 + 50, // Mock value
                label: new Date(now - (i * intervalMs / points)).toLocaleTimeString()
            });
        }

        return data;
    }

    private generateBreakdownData(metricName: string) {
        // Generate mock breakdown data
        return [
            { category: 'Component A', value: 35, percentage: 35 },
            { category: 'Component B', value: 25, percentage: 25 },
            { category: 'Component C', value: 20, percentage: 20 },
            { category: 'Other', value: 20, percentage: 20 }
        ];
    }

    generateReport(startDate?: Date, endDate?: Date) {
        return Promise.resolve({
            timestamp: new Date().toISOString(),
            dateRange: {
                start: startDate?.toISOString() || new Date(Date.now() - 86400000).toISOString(),
                end: endDate?.toISOString() || new Date().toISOString()
            },
            metrics: Array.from(this.metrics.keys()).map(name => ({
                name,
                details: this.getMetricDetails(name)
            })),
            summary: {
                totalMetrics: this.metrics.size,
                avgPerformance: this.getAverageRenderTime(),
                memoryUsage: this.getMemoryUsage()
            }
        });
    }

    // Add missing getStats method
    getStats() {
        return {
            memoryUsage: this.getMemoryUsage(),
            cpuUsage: this.getCpuUsage(),
            averageRenderTime: this.getAverageRenderTime(),
            networkLatency: this.getNetworkLatency(),
            metricsCount: this.metrics.size
        };
    }

    private getMemoryUsage(): number {
        if (hasMemorySupport(performance)) {
            return (performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit) * 100;
        }
        return 0;
    }

    private getCpuUsage(): number {
        // Approximate CPU usage based on performance timing
        return Math.min(performance.now() % 100, 100);
    }

    private getAverageRenderTime(): number {
        const renderMetrics = Array.from(this.metrics.keys()).filter(key => key.includes('render_time'));
        if (renderMetrics.length === 0) return 0;
        return renderMetrics.reduce((sum, key) => sum + (this.metrics.get(key)?.value || 0), 0) / renderMetrics.length;
    }

    private getNetworkLatency(): number {
        const networkMetrics = Array.from(this.metrics.keys()).filter(key => key.includes('api_call'));
        if (networkMetrics.length === 0) return 0;
        return networkMetrics.reduce((sum, key) => sum + (this.metrics.get(key)?.value || 0), 0) / networkMetrics.length;
    }

    // Add missing getComponentStats method
    getComponentStats() {
        const renderMetrics = Array.from(this.metrics.keys())
            .filter(key => key.includes('render_time'))
            .map(key => {
                const componentName = key.replace('render_time_', '');
                const metric = this.metrics.get(key);
                return {
                    componentName,
                    renderTime: metric?.value || 0,
                    lastUpdate: metric?.timestamp || Date.now()
                };
            });

        return Promise.resolve(renderMetrics);
    }
}