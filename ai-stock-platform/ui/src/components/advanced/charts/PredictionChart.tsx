/**
 * Prediction Chart Component
 * Created: 2025-06-19 03:13:52
 * Author: daparthi001
 */
import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import { PredictionResult } from '../../../services/ml-service';

interface PredictionChartProps {
  symbol: string;
  prediction: PredictionResult[];
}

const PredictionChart: React.FC<PredictionChartProps> = ({ symbol, prediction }) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);
  
  useEffect(() => {
    if (!chartRef.current || !prediction) return;
    
    // Destroy previous chart if it exists
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }
    
    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;
    
    // Format dates for display
    const dates = prediction.map(p => {
      const date = new Date(p.date);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    // Extract price data
    const predictedPrices = prediction.map(p => p.predicted_price);
    const upperBounds = prediction.map(p => p.upper_bound || 0);
    const lowerBounds = prediction.map(p => p.lower_bound || 0);
    
    // Add historical data point for better visualization
    // This would typically come from real data
    const historicalPrice = predictedPrices[0] * 0.98; // Placeholder
    dates.unshift('Current');
    predictedPrices.unshift(historicalPrice);
    upperBounds.unshift(historicalPrice);
    lowerBounds.unshift(historicalPrice);
    
    // Create gradient fill for the area between upper and lower bounds
    const gradientFill = ctx.createLinearGradient(0, 0, 0, 400);
    gradientFill.addColorStop(0, 'rgba(78, 115, 223, 0.15)');
    gradientFill.addColorStop(1, 'rgba(78, 115, 223, 0.02)');
    
    // Create the chart
    chartInstance.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [
          {
            label: 'Predicted Price',
            data: predictedPrices,
            borderColor: '#4e73df',
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointBackgroundColor: '#4e73df',
            pointBorderColor: '#ffffff',
            pointRadius: 4,
            pointHoverRadius: 6,
            tension: 0.1
          },
          {
            label: 'Upper Bound',
            data: upperBounds,
            borderColor: 'rgba(78, 115, 223, 0.5)',
            borderDash: [5, 5],
            borderWidth: 1,
            pointRadius: 0,
            fill: false,
            tension: 0.1
          },
          {
            label: 'Lower Bound',
            data: lowerBounds,
            borderColor: 'rgba(78, 115, 223, 0.5)',
            borderDash: [5, 5],
            borderWidth: 1,
            pointRadius: 0,
            backgroundColor: gradientFill,
            fill: '+1', // Fill between this dataset and the next one
            tension: 0.1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              boxWidth: 12,
              usePointStyle: true,
              pointStyle: 'circle'
            }
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
              display: true
            },
            title: {
              display: true,
              text: 'Price (USD)'
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
  }, [symbol, prediction]);
  
  return (
    <canvas ref={chartRef} />
  );
};

export default PredictionChart;