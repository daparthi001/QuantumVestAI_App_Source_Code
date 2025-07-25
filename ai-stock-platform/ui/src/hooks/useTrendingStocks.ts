import { useEffect, useState } from 'react';
import apiService, { Stock } from '../services/api-service';
import wsService from '../services/websocket.service';

interface TrendingState {
  stocks: Stock[];
  lastUpdate: string;
  loading: boolean;
  error: string | null;
}

export const useTrendingStocks = (limit = 10): TrendingState => {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState('');

  useEffect(() => {
    let mounted = true;

    const fetchInitial = async () => {
      try {
        setLoading(true);
        const data = await apiService.getTrendingStocks();
        if (mounted) {
          setStocks(data.slice(0, limit));
          setLastUpdate(new Date().toISOString());
        }
      } catch (err) {
        console.error('Error fetching trending stocks:', err);
        if (mounted) {
          setError('Failed to load trending stocks');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    fetchInitial();

    const handleUpdate = (data: Stock[]) => {
      if (mounted) {
        setStocks(data.slice(0, limit));
        setLastUpdate(new Date().toISOString());
      }
    };

    wsService.subscribe('trending_stocks', handleUpdate);

    return () => {
      mounted = false;
      wsService.unsubscribe('trending_stocks');
    };
  }, [limit]);

  return { stocks, lastUpdate, loading, error };
};

export default useTrendingStocks;
