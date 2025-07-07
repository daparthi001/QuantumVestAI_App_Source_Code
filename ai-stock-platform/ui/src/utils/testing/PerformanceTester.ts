/**
 * Performance Testing Utility
 * Created: 2025-05-19 05:06:36
 * Author: daparthi001
 */
import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { PerformanceMonitor } from '../../services/monitoring/PerformanceMonitor';


// Extend Performance interface to include memory property
interface PerformanceWithMemory extends Performance {
    memory?: {
        usedJSHeapSize: number;
        totalJSHeapSize: number;
        jsHeapSizeLimit: number;
    };
}

// Type guard to check if performance.memory is available
function hasMemorySupport(perf: Performance): perf is PerformanceWithMemory {
    return 'memory' in perf;
}


export class PerformanceTester {
    private static instance: PerformanceTester;
    private monitor: PerformanceMonitor;
    private testResults: Map<string, PerformanceTestResult[]> = new Map();

    private constructor() {
        this.monitor = PerformanceMonitor.getInstance();
    }

    static getInstance(): PerformanceTester {
        if (!PerformanceTester.instance) {
            PerformanceTester.instance = new PerformanceTester();
        }
        return PerformanceTester.instance;
    }

    async measureRenderTime(
        component: React.ComponentType,
        props: any,
        iterations: number = 100
    ): Promise<PerformanceTestResult> {
        const results: number[] = [];

        for (let i = 0; i < iterations; i++) {
            const start = performance.now();
            await this.renderComponent(component, props);
            const end = performance.now();
            results.push(end - start);
        }

        const testResult = this.calculateStats(results);
        this.storeResult('render', testResult);
        return testResult;
    }

    async measureOperationTime(
        operation: () => Promise<void>,
        name: string,
        iterations: number = 100
    ): Promise<PerformanceTestResult> {
        const results: number[] = [];

        for (let i = 0; i < iterations; i++) {
            const start = performance.now();
            await operation();
            const end = performance.now();
            results.push(end - start);
        }

        const testResult = this.calculateStats(results);
        this.storeResult(name, testResult);
        return testResult;
    }

    async measureMemoryUsage(
        operation: () => Promise<void>
    ): Promise<MemoryTestResult> {

        if (!hasMemorySupport(performance) || !performance.memory) {

            throw new Error('Memory measurements not supported in this environment');
        }

        const initialMemory = perfMemory.usedJSHeapSize;
        await operation();
        const finalMemory = perfMemory.usedJSHeapSize;

        return {
            beforeBytes: initialMemory,
            afterBytes: finalMemory,
            differenceBytes: finalMemory - initialMemory
        };
    }

    async generateReport(testName: string): Promise<TestReport> {
        const results = this.testResults.get(testName) || [];
        const recentResults = results.slice(-10);

        return {
            testName,
            timestamp: new Date().toISOString(),
            results: recentResults,
            trend: this.calculateTrend(recentResults),
            recommendations: this.generateRecommendations(recentResults)
        };
    }

    private async renderComponent(
        component: React.ComponentType,
        props: any
    ): Promise<void> {
        const div = document.createElement('div');
        document.body.appendChild(div);
        
        try {

            await new Promise<void>((resolve) => {
                const element = React.createElement(component, props);
                ReactDOM.render(element, div, () => {
                    resolve();
                });
        } finally {
            ReactDOM.unmountComponentAtNode(div);
            document.body.removeChild(div);
        }
    }

    private calculateStats(results: number[]): PerformanceTestResult {
        const sorted = [...results].sort((a, b) => a - b);
        return {
            min: sorted[0],
            max: sorted[sorted.length - 1],
            mean: results.reduce((a, b) => a + b) / results.length,
            median: sorted[Math.floor(sorted.length / 2)],
            p95: sorted[Math.floor(sorted.length * 0.95)],
            standardDeviation: this.calculateStandardDeviation(results)
        };
    }

    private calculateStandardDeviation(values: number[]): number {
        const mean = values.reduce((a, b) => a + b) / values.length;
        const squareDiffs = values.map(value => (value - mean) ** 2);
        return Math.sqrt(squareDiffs.reduce((a, b) => a + b) / values.length);
    }

    private calculateTrend(results: PerformanceTestResult[]): 'improving' | 'stable' | 'degrading' {
        if (results.length < 2) return 'stable';
        
        const recentMean = results[results.length - 1].mean;
        const previousMean = results[results.length - 2].mean;
        const difference = ((recentMean - previousMean) / previousMean) * 100;

        if (difference < -5) return 'improving';
        if (difference > 5) return 'degrading';
        return 'stable';
    }

    private generateRecommendations(results: PerformanceTestResult[]): string[] {
        const recommendations: string[] = [];
        const latestResult = results[results.length - 1];

        if (latestResult.mean > 100) {
            recommendations.push('Consider implementing performance optimizations');
        }
        if (latestResult.standardDeviation > latestResult.mean * 0.2) {
            recommendations.push('High variability detected, investigate inconsistent behavior');
        }
        if (latestResult.p95 > latestResult.mean * 2) {
            recommendations.push('Large outliers present, consider implementing error boundaries');
        }

        return recommendations;
    }

    private storeTestResult(testName: string, result: PerformanceTestResult): void {
        if (!this.testResults.has(testName)) {
            this.testResults.set(testName, []);
        }
        const results = this.testResults.get(testName)!;
        results.push(result);
        
        // Keep only the last 50 results to prevent memory issues
        if (results.length > 50) {
            results.shift();
        }

        // Use the monitor to track performance metrics
        this.monitor.trackRenderTime(testName, result.mean);

    }
}

interface PerformanceTestResult {
    min: number;
    max: number;
    mean: number;
    median: number;
    p95: number;
    standardDeviation: number;
}

interface MemoryTestResult {
    beforeBytes: number;
    afterBytes: number;
    differenceBytes: number;
}

interface TestReport {
    testName: string;
    timestamp: string;
    results: PerformanceTestResult[];
    trend: 'improving' | 'stable' | 'degrading';
    recommendations: string[];
}