/**
 * Global Type Definitions
 * Created: 2025-01-27
 * Author: daparthi001
 */

// Extend Performance interface to include memory property
declare global {
  interface Performance {
    memory?: {
      usedJSHeapSize: number;
      totalJSHeapSize: number;
      jsHeapSizeLimit: number;
    };
  }
}

// Type guard to check if performance.memory is available
export function hasMemorySupport(perf: Performance): perf is Performance & { memory: NonNullable<Performance['memory']> } {
  return 'memory' in perf && perf.memory !== undefined;
}

export {};