/**
 * Performance Monitoring Service
 * Created: 2025-05-19 05:01:47
 * Author: daparthi001
 */
import { trace, context, SpanStatusCode } from '@opentelemetry/api';
import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';
import { Metric } from '@opentelemetry/metrics';

export class PerformanceMonitor {
    private static instance: PerformanceMonitor;
    private metrics: Map<string, Metric>;

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
        // Initialize OpenTelemetry tracing
        const tracer = trace.getTracer('order-management-ui');
        context.setGlobalContextManager(tracer);
    }

    trackOrderOperation(operation: string, duration: number, success: boolean) {
        const span = trace.getSpan(context.active());
        if (span) {
            span.setAttribute('operation', operation);
            span.setAttribute('duration_ms', duration);
            span.setStatus(success ? SpanStatusCode.OK : SpanStatusCode.ERROR);
        }

        // Record metric
        this.recordMetric(`order_operation_${operation}`, duration);
    }

    trackRenderTime(componentName: string, duration: number) {
        if (duration > 16.67) { // Longer than one frame (60fps)
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
            const meter = trace.getMeter('order-management-ui');
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

// HOC for component performance monitoring
export function withPerformanceTracking<P extends object>(
    WrappedComponent: React.ComponentType<P>,
    componentName: string
) {
    return class extends React.Component<P> {
        private renderStart: number = 0;
        private monitor = PerformanceMonitor.getInstance();

        componentDidMount() {
            const renderTime = performance.now() - this.renderStart;
            this.monitor.trackRenderTime(componentName, renderTime);
        }

        componentDidUpdate() {
            const renderTime = performance.now() - this.renderStart;
            this.monitor.trackRenderTime(componentName, renderTime);
        }

        render() {
            this.renderStart = performance.now();
            return <WrappedComponent {...this.props} />;
        }
    };
}