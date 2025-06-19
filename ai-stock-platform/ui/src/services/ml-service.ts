/**
 * Machine Learning Service
 * Created: 2025-06-19 03:09:13
 * Author: daparthi001
 */
import { api } from './api';

export interface PredictionResult {
  symbol: string;
  date: string;
  predicted_price: number;
  confidence: number;
  prediction_type: 'next_day' | 'week_ahead' | 'month_ahead';
  model_version: string;
  features_used: string[];
  upper_bound?: number;
  lower_bound?: number;
}

export interface ModelInfo {
  id: string;
  name: string;
  version: string;
  algorithm: string;
  accuracy: number;
  last_trained: string;
  features: string[];
  description: string;
  status: 'active' | 'training' | 'deprecated';
}

export const mlService = {
  /**
   * Get price prediction for a stock
   */
  async getPrediction(symbol: string, predictionType: 'next_day' | 'week_ahead' | 'month_ahead'): Promise<PredictionResult> {
    try {
      const response = await api.get(`/predictions/${symbol}`, {
        params: { type: predictionType }
      });
      return response.data.data;
    } catch (error) {
      console.error(`Error fetching prediction for ${symbol}:`, error);
      throw error;
    }
  },

  /**
   * Get multiple predictions for a date range
   */
  async getPredictionRange(
    symbol: string, 
    startDate: string, 
    endDate: string, 
    modelId?: string
  ): Promise<PredictionResult[]> {
    try {
      const response = await api.get(`/predictions/${symbol}/range`, {
        params: { 
          start_date: startDate, 
          end_date: endDate,
          model_id: modelId 
        }
      });
      return response.data.data;
    } catch (error) {
      console.error(`Error fetching prediction range for ${symbol}:`, error);
      throw error;
    }
  },

  /**
   * Get available ML models information
   */
  async getModels(): Promise<ModelInfo[]> {
    try {
      const response = await api.get('/models');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching ML models:', error);
      throw error;
    }
  },

  /**
   * Get accuracy metrics for a specific model
   */
  async getModelMetrics(modelId: string): Promise<any> {
    try {
      const response = await api.get(`/models/${modelId}/metrics`);
      return response.data.data;
    } catch (error) {
      console.error(`Error fetching metrics for model ${modelId}:`, error);
      throw error;
    }
  },

  /**
   * Request a new model training job
   */
  async requestModelTraining(
    symbols: string[], 
    features: string[],
    algorithm: string,
    parameters: Record<string, any>
  ): Promise<{ job_id: string }> {
    try {
      const response = await api.post('/models/train', {
        symbols,
        features,
        algorithm,
        parameters
      });
      return response.data.data;
    } catch (error) {
      console.error('Error requesting model training:', error);
      throw error;
    }
  }
};