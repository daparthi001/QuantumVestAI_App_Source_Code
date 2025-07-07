/**
 * Load Test Types
 * Created: 2025-01-08
 * Author: daparthi001
 */

export interface TestMetrics {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  minResponseTime: number;
  maxResponseTime: number;
  requestsPerSecond: number;
  errorRate: number;
  throughput: number;
  concurrency: number;
  startTime: number;
  endTime: number;
}

export interface TestResult {
  id: string;
  testName: string;
  status: 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  metrics: TestMetrics;
  errors: TestError[];
  startTime: number;
  endTime?: number;
  duration?: number;
}

export interface TestError {
  timestamp: number;
  message: string;
  statusCode?: number;
  endpoint?: string;
  type: 'NETWORK' | 'TIMEOUT' | 'SERVER' | 'CLIENT' | 'UNKNOWN';
}

export interface TestStep {
  id: string;
  name: string;
  type: 'REQUEST' | 'ASSERTION' | 'WAIT' | 'SCRIPT';
  config: any;
  expectedResult?: any;
  actualResult?: any;
  status?: 'PENDING' | 'RUNNING' | 'PASSED' | 'FAILED';
  duration?: number;
  assertions?: any[];
}

export interface TestScenario {
  id: string;
  name: string;
  description: string;
  steps: TestStep[];
  concurrency: number;
  duration: number;
  rampUp: number;
  rampDown: number;
}

export interface LoadTestConfig {
  name: string;
  scenarios: TestScenario[];
  globalTimeout: number;
  maxConcurrency: number;
  reporting: {
    interval: number;
    includeRequestDetails: boolean;
    includeResponseDetails: boolean;
  };
}