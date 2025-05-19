/**
 * Load Test Worker
 * Created: 2025-05-19 05:09:34
 * Author: daparthi001
 */
import { LoadTestConfig, TestScenario, TestStep } from '../types/loadTest';

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
            this.handleTestError(testId, error);
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
                userId: this.userId,
                scenarioName: scenario.name,
                duration: Date.now() - startTime,
                success: true
            };
        } catch (error) {
            return {
                userId: this.userId,
                scenarioName: scenario.name,
                duration: Date.now() - startTime,
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error'
            };
        }
    }

    private selectScenario(): TestScenario {
        const totalWeight = this.scenarios.reduce((sum, s) => sum + s.weight, 0);
        let random = Math.random() * totalWeight;

        for (const scenario of this.scenarios) {
            random -= scenario.weight;
            if (random <= 0) return scenario;
        }

        return this.scenarios[0];
    }

    private async executeStep(step: TestStep): Promise<void> {
        switch (step.type) {
            case 'request':
                await this.executeRequest(step);
                break;
            case 'action':
                await this.executeAction(step);
                break;
        }
    }

    private async executeRequest(step: TestStep): Promise<void> {
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
        // Simulate user actions
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
        return true;
    }
}

class MetricCollector {
    private metrics: TestMetrics = {
        requestCount: 0,
        successCount: 0,
        failureCount: 0,
        totalDuration: 0,
        minDuration: Infinity,
        maxDuration: 0,
        scenarios: new Map()
    };

    addMetric(result: TestResult) {
        this.metrics.requestCount++;
        if (result.success) {
            this.metrics.successCount++;
        } else {
            this.metrics.failureCount++;
        }

        this.metrics.totalDuration += result.duration;
        this.metrics.minDuration = Math.min(this.metrics.minDuration, result.duration);
        this.metrics.maxDuration = Math.max(this.metrics.maxDuration, result.duration);

        // Update scenario metrics
        const scenarioMetrics = this.metrics.scenarios.get(result.scenarioName) || {
            count: 0,
            successCount: 0,
            totalDuration: 0
        };
        scenarioMetrics.count++;
        if (result.success) scenarioMetrics.successCount++;
        scenarioMetrics.totalDuration += result.duration;
        this.metrics.scenarios.set(result.scenarioName, scenarioMetrics);
    }

    getCurrentMetrics(): TestMetrics {
        return {...this.metrics};
    }

    getFinalMetrics(): TestMetrics {
        return {
            ...this.metrics,
            averageDuration: this.metrics.totalDuration / this.metrics.requestCount,
            successRate: this.metrics.successCount / this.metrics.requestCount
        };
    }
}

// Initialize the worker
new LoadTestWorker();