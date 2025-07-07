/**
 * Performance Testing Utility
 * Created: 2025-05-19 05:06:36
 * Author: daparthi001
 */
import React from 'react';
import ReactDOM from 'react-dom';
import { PerformanceMonitor } from '../../services/monitoring/PerformanceMonitor';
import { TestResult } from '../../types/loadTest';

export class PerformanceTester {
    private static instance: PerformanceTester;
    private monitor: PerformanceMonitor;
    private testResults: Map<string, TestResult[]> = new Map();

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
    ): Promise<TestResult> {
        const results: number[] = [];

        for (let i = 0; i < iterations; i++) {
            const start = performance.now();
            await this.renderComponent(component, props);
            const end = performance.now();
            results.push(end - start);
        }

        const testResult = this.calculateStats(results);
        this.storeTestResult('render', testResult);
        return testResult;
    }

    async measureOperationTime(
        operation: () => Promise<void>,
        name: string,
        iterations: number = 100
    ): Promise<TestResult> {
        const results: number[] = [];

        for (let i = 0; i < iterations; i++) {
            const start = performance.now();
            await operation();
            const end = performance.now();
            results.push(end - start);
        }

        const testResult = this.calculateStats(results);
        this.storeTestResult(name, testResult);
        return testResult;
    }

    async measureMemoryUsage(
        operation: () => Promise<void>
    ): Promise<MemoryTestResult> {
        const perfMemory = (performance as any).memory;
        if (!perfMemory) {
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
        try {
            await new Promise(resolve => {
                ReactDOM.render(
                    React.createElement(component, props),
                    div,
                    resolve
                );
            });
        } finally {
            ReactDOM.unmountComponentAtNode(div);
        }
    }

    private calculateStats(results: number[]): TestResult {
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

    private calculateTrend(results: TestResult[]): 'improving' | 'stable' | 'degrading' {
        if (results.length < 2) return 'stable';
        
        const recentMean = results[results.length - 1].mean;
        const previousMean = results[results.length - 2].mean;
        const difference = ((recentMean - previousMean) / previousMean) * 100;

        if (difference < -5) return 'improving';
        if (difference > 5) return 'degrading';
        return 'stable';
    }

    private generateRecommendations(results: TestResult[]): string[] {
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
}

interface TestResult {
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
    results: TestResult[];
    trend: 'improving' | 'stable' | 'degrading';
    recommendations: string[];
}