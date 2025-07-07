/**
 * Load Test Worker
 * Created: 2025-05-19 05:09:34
 * Author: daparthi001
 */
import { LoadTestConfig, TestScenario, TestStep, TestMetrics, TestResult } from '../types/loadTest';

class LoadTestWorker {
    private activeTests: Map<string, boolean> = new Map();
    private metrics: Map<string, MetricCollector> = new Map();

    constructor() {
        self.onmessage = this.handleMessage.bind(this);
    }

    private async handleMessage(event: MessageEvent) {
        const { type, payload } = event.data;

        switch (type) {
            case 'START_TEST':
                await this.startTest(payload.testId, payload.config);
                break;
            case 'STOP_TEST':
                this.stopTest(payload.testId);
                break;
        }
    }

    private async startTest(testId: string, config: LoadTestConfig) {
        this.activeTests.set(testId, true);
        this.metrics.set(testId, new MetricCollector());

        try {
            // Initialize virtual users
            const users = await this.createVirtualUsers(config);
            
            // Start test execution
            await this.executeLoadTest(testId, users, config);
            
        } catch (error) {
            this.handleTestError(testId, error instanceof Error ? error : new Error(String(error)));
        }
    }

    private async createVirtualUsers(config: LoadTestConfig): Promise<VirtualUser[]> {
        const users: VirtualUser[] = [];
        const usersPerBatch = Math.ceil(config.users / (config.rampUpTime / 1000));

        for (let i = 0; i < config.users; i++) {
            const user = new VirtualUser(i, config.scenarios);
            users.push(user);

            if ((i + 1) % usersPerBatch === 0) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }

        return users;
    }

    private async executeLoadTest(
        testId: string,
        users: VirtualUser[],
        config: LoadTestConfig
    ) {
        const startTime = Date.now();
        const collector = this.metrics.get(testId)!;

        while (
            this.activeTests.get(testId) &&
            Date.now() - startTime < config.duration
        ) {
            const executions = users.map(user => user.executeScenario());
            const results = await Promise.all(executions);

            // Collect and report metrics
            results.forEach(result => collector.addMetric(result));
            this.reportProgress(testId, collector.getCurrentMetrics());

            // Apply think time
            await new Promise(resolve => 
                setTimeout(resolve, config.thinkTime)
            );
        }

        this.finalizeTest(testId);
    }

    private stopTest(testId: string) {
        this.activeTests.set(testId, false);
    }

    private handleTestError(testId: string, error: Error) {
        self.postMessage({
            type: 'TEST_ERROR',
            payload: {
                testId,
                error: error.message
            }
        });
    }

    private reportProgress(testId: string, metrics: TestMetrics) {
        self.postMessage({
            type: 'TEST_PROGRESS',
            payload: {
                testId,
                metrics
            }
        });
    }

    private finalizeTest(testId: string) {
        const finalMetrics = this.metrics.get(testId)?.getFinalMetrics();
        
        self.postMessage({
            type: 'TEST_COMPLETE',
            payload: {
                testId,
                metrics: finalMetrics
            }
        });

        // Cleanup
        this.activeTests.delete(testId);
        this.metrics.delete(testId);
    }
}

class VirtualUser {
    private userId: number;
    private scenarios: TestScenario[];
    private currentScenario: number = 0;

    constructor(userId: number, scenarios: TestScenario[]) {
        this.userId = userId;
        this.scenarios = scenarios;
    }

    async executeScenario(): Promise<TestResult> {
        const startTime = Date.now();
        const scenario = this.selectScenario();

        try {
            for (const step of scenario.steps) {
                await this.executeStep(step);
            }

            return {
                id: `${this.userId}-${scenario.id}`,
                testName: scenario.name,
                status: 'COMPLETED',
                metrics: {
                    totalRequests: 1,
                    successfulRequests: 1,
                    failedRequests: 0,
                    averageResponseTime: Date.now() - startTime,
                    minResponseTime: Date.now() - startTime,
                    maxResponseTime: Date.now() - startTime,
                    requestsPerSecond: 1,
                    errorRate: 0,
                    throughput: 1,
                    concurrency: 1,
                    startTime,
                    endTime: Date.now()
                },
                errors: [],
                startTime,
                endTime: Date.now(),
                duration: Date.now() - startTime,
                userId: this.userId.toString()
            };
        } catch (error) {
            return {
                id: `${this.userId}-${scenario.id}`,
                testName: scenario.name,
                status: 'FAILED',
                metrics: {
                    totalRequests: 1,
                    successfulRequests: 0,
                    failedRequests: 1,
                    averageResponseTime: Date.now() - startTime,
                    minResponseTime: Date.now() - startTime,
                    maxResponseTime: Date.now() - startTime,
                    requestsPerSecond: 1,
                    errorRate: 1,
                    throughput: 0,
                    concurrency: 1,
                    startTime,
                    endTime: Date.now()
                },
                errors: [{
                    timestamp: Date.now(),
                    message: error instanceof Error ? error.message : String(error),
                    type: 'UNKNOWN'
                }],
                startTime,
                endTime: Date.now(),
                duration: Date.now() - startTime,
                userId: this.userId.toString()
            };
        }
    }

    private selectScenario(): TestScenario {
        // Use currentScenario to rotate through scenarios
        const scenario = this.scenarios[this.currentScenario % this.scenarios.length];
        this.currentScenario++;
        return scenario;
    }

    private async executeStep(step: TestStep): Promise<void> {
        switch (step.type) {
            case 'REQUEST':
                await this.executeRequest(step);
                break;
            case 'SCRIPT':
                await this.executeAction(step);
                break;
            case 'WAIT':
                await new Promise(resolve => setTimeout(resolve, 1000));
                break;
            case 'ASSERTION':
                // Handle assertions
                break;
        }
    }

    private async executeRequest(step: TestStep): Promise<void> {
        if (!step.target) return;
        
        const response = await fetch(step.target, {
            method: step.method || 'GET',
            body: step.data ? JSON.stringify(step.data) : undefined,
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Request failed: ${response.status}`);
        }

        if (step.assertions) {
            await this.validateAssertions(step.assertions, response);
        }
    }

    private async executeAction(step: TestStep): Promise<void> {
        // Simulate user actions based on step type
        console.log(`Executing action: ${step.name}`);
        await new Promise(resolve => setTimeout(resolve, 100));
    }

    private async validateAssertions(assertions: any[], response: Response) {
        for (const assertion of assertions) {
            switch (assertion.type) {
                case 'status':
                    if (response.status !== assertion.value) {
                        throw new Error(
                            `Status assertion failed: ${response.status} !== ${assertion.value}`
                        );
                    }
                    break;
                case 'response':
                    const data = await response.json();
                    if (!this.evaluateCondition(data, assertion.condition, assertion.value)) {
                        throw new Error(`Response assertion failed: ${assertion.condition}`);
                    }
                    break;
            }
        }
    }

    private evaluateCondition(data: any, condition: string, value: any): boolean {
        // Implement condition evaluation logic
        switch (condition) {
            case 'equals':
                return data === value;
            case 'greater':
                return data > value;
            case 'less':
                return data < value;
            default:
                return true;
        }
    }
}

class MetricCollector {
    private metrics: TestMetrics = {
        totalRequests: 0,
        successfulRequests: 0,
        failedRequests: 0,
        averageResponseTime: 0,
        minResponseTime: Infinity,
        maxResponseTime: 0,
        requestsPerSecond: 0,
        errorRate: 0,
        throughput: 0,
        concurrency: 0,
        startTime: Date.now(),
        endTime: 0
    };

    addMetric(result: TestResult) {
        this.metrics.totalRequests++;
        if (result.status === 'COMPLETED') {
            this.metrics.successfulRequests++;
        } else {
            this.metrics.failedRequests++;
        }

        // Update response time metrics if duration is available
        if (result.duration) {
            this.metrics.minResponseTime = Math.min(this.metrics.minResponseTime, result.duration);
            this.metrics.maxResponseTime = Math.max(this.metrics.maxResponseTime, result.duration);
        }

        // Calculate averages
        this.metrics.errorRate = this.metrics.failedRequests / this.metrics.totalRequests;
        this.metrics.endTime = Date.now();
        const testDuration = (this.metrics.endTime - this.metrics.startTime) / 1000;
        this.metrics.requestsPerSecond = this.metrics.totalRequests / testDuration;
    }

    getCurrentMetrics(): TestMetrics {
        return {...this.metrics};
    }

    getFinalMetrics(): TestMetrics {
        return {
            ...this.metrics,
            averageResponseTime: this.metrics.totalRequests > 0 ? 
                (this.metrics.endTime - this.metrics.startTime) / this.metrics.totalRequests : 0
        };
    }
}

// Initialize the worker
new LoadTestWorker();