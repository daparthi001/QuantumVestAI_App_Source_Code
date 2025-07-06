import { trace, context, SpanStatusCode, metrics, Histogram } from '@opentelemetry/api';
import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';

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
            integrations: [new BrowserTracing()],
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
}