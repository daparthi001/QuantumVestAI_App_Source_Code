/**
 * Load Testing Service
 * Created: 2025-05-19 05:08:03
 * Author: daparthi001
 */
import { RealTimeMonitor } from '../monitoring/RealTimeMonitor';
import { PerformanceMonitor } from '../monitoring/PerformanceMonitor';

export class LoadTester {
    private static instance: LoadTester;
    private monitor: RealTimeMonitor;
    private performanceMonitor: PerformanceMonitor;
    private activeTests: Map<string, TestSession>;
    private worker: Worker | null = null;

    private constructor() {
        this.monitor = RealTimeMonitor.getInstance();
        this.performanceMonitor = PerformanceMonitor.getInstance();
        this.activeTests = new Map();
        this.initializeWorker();
    }

    static getInstance(): LoadTester {
        if (!LoadTester.instance) {
            LoadTester.instance = new LoadTester();
        }
        return LoadTester.instance;
    }

    private initializeWorker() {
        this.worker = new Worker('./loadTestWorker.ts');
        this.worker.onmessage = this.handleWorkerMessage.bind(this);
    }

    async startLoadTest(config: LoadTestConfig): Promise<string> {
        const testId = `loadtest-${Date.now()}`;
        const session: TestSession = {
            id: testId,
            config,
            startTime: Date.now(),
            results: [],
            status: 'running'
        };

        this.activeTests.set(testId, session);

        // Start test in worker
        this.worker?.postMessage({
            type: 'START_TEST',
            payload: {
                testId,
                config
            }
        });

        return testId;
    }

    async stopTest(testId: string): Promise<TestResults | null> {
        const session = this.activeTests.get(testId);
        if (!session) return null;

        session.status = 'stopped';
        this.worker?.postMessage({
            type: 'STOP_TEST',
            payload: { testId }
        });

        return this.generateTestResults(session);
    }

    private handleWorkerMessage(event: MessageEvent) {
        const { type, payload } = event.data;

        switch (type) {
            case 'TEST_PROGRESS':
                this.updateTestProgress(payload);
                break;
            case 'TEST_ERROR':
                this.handleTestError(payload);
                break;
            case 'TEST_COMPLETE':
                this.finalizeTest(payload);
                break;
        }
    }

    private updateTestProgress(payload: any) {
        const { testId, metrics } = payload;
        const session = this.activeTests.get(testId);
        if (session) {
            session.results.push(metrics);
            this.monitor.trackMetric('load_test_progress', metrics);
        }
    }

    private handleTestError(payload: any) {
        const { testId, error } = payload;
        const session = this.activeTests.get(testId);
        if (session) {
            session.status = 'error';
            session.error = error;
        }
    }

    private async finalizeTest(payload: any) {
        const { testId } = payload;
        const session = this.activeTests.get(testId);
        if (session) {
            session.status = 'completed';
            session.endTime = Date.now();
            
            const results = await this.generateTestResults(session);
            this.monitor.trackMetric('load_test_complete', results);
        }
    }

    private async generateTestResults(session: TestSession): Promise<TestResults> {
        const duration = (session.endTime || Date.now()) - session.startTime;
        const metrics = this.aggregateMetrics(session.results);

        return {
            testId: session.id,
            duration,
            metrics,
            status: session.status,
            error: session.error,
            recommendations: await this.generateRecommendations(metrics)
        };
    }

    private aggregateMetrics(results: any[]): AggregatedMetrics {
        // Calculate aggregate statistics
        return results.reduce((acc, curr) => ({
            averageResponseTime: acc.averageResponseTime + curr.responseTime,
            throughput: acc.throughput + curr.requestsPerSecond,
            errorRate: acc.errorRate + curr.errorRate,
            concurrentUsers: Math.max(acc.concurrentUsers, curr.concurrentUsers)
        }), {
            averageResponseTime: 0,
            throughput: 0,
            errorRate: 0,
            concurrentUsers: 0
        });
    }

    private async generateRecommendations(
        metrics: AggregatedMetrics
    ): Promise<string[]> {
        const recommendations: string[] = [];

        if (metrics.averageResponseTime > 1000) {
            recommendations.push(
                'Response times are high. Consider implementing caching or optimization.'
            );
        }

        if (metrics.errorRate > 0.05) {
            recommendations.push(
                'Error rate is above 5%. Review error handling and retry mechanisms.'
            );
        }

        if (metrics.throughput < metrics.concurrentUsers) {
            recommendations.push(
                'Throughput is lower than expected. Consider scaling resources.'
            );
        }

        return recommendations;
    }
}

interface LoadTestConfig {
    targetUrl: string;
    duration: number;
    users: number;
    rampUpTime: number;
    thinkTime: number;
    scenarios: TestScenario[];
}

interface TestScenario {
    name: string;
    weight: number;
    steps: TestStep[];
}

interface TestStep {
    type: 'request' | 'action';
    target: string;
    method?: string;
    data?: any;
    assertions?: TestAssertion[];
}

interface TestAssertion {
    type: 'status' | 'response' | 'performance';
    condition: string;
    value: any;
}

interface TestSession {
    id: string;
    config: LoadTestConfig;
    startTime: number;
    endTime?: number;
    results: any[];
    status: 'running' | 'completed' | 'error' | 'stopped';
    error?: Error;
}

interface TestResults {
    testId: string;
    duration: number;
    metrics: AggregatedMetrics;
    status: string;
    error?: Error;
    recommendations: string[];
}

interface AggregatedMetrics {
    averageResponseTime: number;
    throughput: number;
    errorRate: number;
    concurrentUsers: number;
}