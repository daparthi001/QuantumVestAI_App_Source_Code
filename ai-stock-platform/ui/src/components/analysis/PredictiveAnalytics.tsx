/**
 * Predictive Analytics Component
 * Displays AI predictions in a chart
 */
import React, { useState, useEffect } from 'react';
import { Card, Spinner, Alert } from 'react-bootstrap';
import { Line } from 'react-chartjs-2';
import apiService from '../../services/api-service';

interface PredictiveAnalyticsProps {
  symbols?: string[];
}

const PredictiveAnalytics: React.FC<PredictiveAnalyticsProps> = ({ symbols = ['AAPL'] }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chartData, setChartData] = useState<any>(null);

  useEffect(() => {
    fetchPredictiveData();
  }, [symbols.join(',')]);

  const fetchPredictiveData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getPredictiveAnalytics(symbols);
      if (!data || !data.predictions?.length) {
        throw new Error('No prediction data');
      }
      const labels = data.predictions.map((p: any) => p.symbol);
      const targets = data.predictions.map((p: any) => p.target);
      setChartData({
        labels,
        datasets: [
          {
            label: 'Predicted Price',
            data: targets,
            borderColor: '#4e73df',
            backgroundColor: 'rgba(78,115,223,0.1)',
            tension: 0.1
          }
        ]
      });
    } catch (err: any) {
      console.error('Error fetching predictive analytics:', err);
      setError('Failed to load predictive analytics');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="mb-4">
      <Card.Header>
        <h5 className="mb-0">Predictive Analysis</h5>
      </Card.Header>
      <Card.Body>
        {loading ? (
          <div className="text-center p-4">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </div>
        ) : error ? (
          <Alert variant="danger">{error}</Alert>
        ) : (
          <div style={{ height: '300px' }}>
            <Line data={chartData} options={{ responsive: true }} />
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default PredictiveAnalytics;
