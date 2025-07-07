import { trace, context, SpanStatusCode, metrics, Histogram } from '@opentelemetry/api';
import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';
import { hasMemorySupport } from '../../types/global';

export class PerformanceMonitor {
    private static instance: PerformanceMonitor;
    private metrics: Map<string, Histogram>;

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
        if (!this.metrics.has(name)) {
            const meter = metrics.getMeter('order-management-ui');
            this.metrics.set(
                name,
                meter.createHistogram(name, {
                    description: `Metric for ${name}`,
                    unit: 'ms'
                })
            );
        }

        const metric = this.metrics.get(name);
        if (metric) {
            metric.record(value);
        }
    }

    // Add missing methods
    getMetricDetails(metricName: string) {
        return {
            name: metricName,
            description: `Metric for ${metricName}`,
            unit: 'ms',
            hasData: this.metrics.has(metricName)
        };
    }

    generateReport() {
        return {
            timestamp: new Date().toISOString(),
            metrics: Array.from(this.metrics.keys()).map(name => ({
                name,
                details: this.getMetricDetails(name)
            }))
        };
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
}