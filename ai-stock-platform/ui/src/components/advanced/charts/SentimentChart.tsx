/**
 * Sentiment Chart Component
 * Created: 2025-06-19 03:13:52
 * Author: daparthi001
 */
import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import { SentimentData } from '../../../services/sentiment-service';

interface SentimentChartProps {
  symbol: string;
  data: SentimentData;
}

const SentimentChart: React.FC<SentimentChartProps> = ({ symbol, data }) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);
  
  useEffect(() => {
    if (!chartRef.current || !data.daily_sentiment) return;
    
    // Destroy previous chart if it exists
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }
    
    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;
    
    // Sort daily sentiment by date
    const sortedData = [...data.daily_sentiment].sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
    
    // Format dates for display
    const dates = sortedData.map(d => {
      const date = new Date(d.date);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    // Extract sentiment scores and volumes
    const sentimentScores = sortedData.map(d => d.sentiment_score);
    const volumes = sortedData.map(d => d.volume);
    
    // Create gradient fill for positive sentiment
    const positiveGradient = ctx.createLinearGradient(0, 0, 0, 200);
    positiveGradient.addColorStop(0, 'rgba(40, 167, 69, 0.4)');
    positiveGradient.addColorStop(1, 'rgba(40, 167, 69, 0.05)');
    
    // Create gradient fill for negative sentiment
    const negativeGradient = ctx.createLinearGradient(0, 0, 0, 200);
    negativeGradient.addColorStop(0, 'rgba(220, 53, 69, 0.4)');
    negativeGradient.addColorStop(1, 'rgba(220, 53, 69, 0.05)');
    
    // Create the chart
    chartInstance.current = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: dates,
        datasets: [
          {
            type: 'line',
            label: 'Sentiment Score',
            data: sentimentScores,
            borderColor: '#6f42c1',
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointBackgroundColor: '#6f42c1',
            pointBorderColor: '#ffffff',
            pointRadius: 4,
            pointHoverRadius: 6,
            tension: 0.1,
            yAxisID: 'y'
          },
          {
            type: 'bar',
            label: 'Volume',
            data: volumes,
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            }
          },
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            min: -1,
            max: 1,
            grid: {
              borderDash: [2, 2]
            },
            title: {
              display: true,
              text: 'Sentiment Score'
            },
            ticks: {
              callback: function(value) {
                if (value === 1) return 'Very Positive';
                if (value === 0.5) return 'Positive';
                if (value === 0) return 'Neutral';
                if (value === -0.5) return 'Negative';
                if (value === -1) return 'Very Negative';
                return '';
              }
            }
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            grid: {
              drawOnChartArea: false
            },
            title: {
              display: true,
              text: 'Volume'
            },
            min: 0
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
  }, [symbol, data]);
  
  return (
    <canvas ref={chartRef} />
  );
};

export default SentimentChart;