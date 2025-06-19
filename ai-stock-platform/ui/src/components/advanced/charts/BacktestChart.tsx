/**
 * Backtest Chart Component
 * Created: 2025-06-19 03:13:52
 * Author: daparthi001
 */
import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

interface BacktestChartProps {
  equityCurve: Array<{date: string, value: number}>;
  benchmarkCurve: Array<{date: string, value: number}>;
}

const BacktestChart: React.FC<BacktestChartProps> = ({ equityCurve, benchmarkCurve }) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);
  
  useEffect(() => {
    if (!chartRef.current || !equityCurve || !benchmarkCurve) return;
    
    // Destroy previous chart if it exists
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }
    
    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;
    
    // Format dates for display
    const dates = equityCurve.map(point => {
      const date = new Date(point.date);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    // Extract values
    const portfolioValues = equityCurve.map(point => point.value);
    const benchmarkValues = benchmarkCurve.map(point => point.value);
    
    // Create gradient fill for portfolio curve
    const portfolioGradient = ctx.createLinearGradient(0, 0, 0, 400);
    portfolioGradient.addColorStop(0, 'rgba(78, 115, 223, 0.3)');
    portfolioGradient.addColorStop(1, 'rgba(78, 115, 223, 0.05)');
    
    // Create the chart
    chartInstance.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [
          {
            label: 'Portfolio',
            data: portfolioValues,
            borderColor: '#4e73df',
            backgroundColor: portfolioGradient,
            borderWidth: 2,
            pointBackgroundColor: '#4e73df',
            pointBorderColor: '#ffffff',
            pointRadius: 0,
            pointHoverRadius: 5,
            tension: 0.1,
            fill: true
          },
          {
            label: 'Benchmark (S&P 500)',
            data: benchmarkValues,
            borderColor: '#858796',
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointBackgroundColor: '#858796',
            pointBorderColor: '#ffffff',
            pointRadius: 0,
            pointHoverRadius: 5,
            tension: 0.1,
            borderDash: [5, 5]
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                if (label) {
                  label += ': ';
                }
                if (context.parsed.y !== null) {
                  label += new Intl.NumberFormat('en-US', { 
                    style: 'currency', 
                    currency: 'USD' 
                  }).format(context.parsed.y);
                }
                return label;
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            }
          },
          y: {
            grid: {
              borderDash: [2, 2]
            },
            title: {
              display: true,
              text: 'Portfolio Value (USD)'
            },
            ticks: {
              callback: function(value) {
                return '$' + value;
              }
            }
          }
        }
      }
    });
    
    // Cleanup on unmount
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [equityCurve, benchmarkCurve]);
  
  return (
    <canvas ref={chartRef} />
  );
};

export default BacktestChart;