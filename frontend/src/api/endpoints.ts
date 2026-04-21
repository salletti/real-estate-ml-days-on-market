import apiClient from './client';
import type {
  PredictionRequest,
  PredictionResponse,
  AllPredictionsResponse,
  ModelInfo,
} from '../types';

export async function fetchPrediction(
  data: PredictionRequest,
  model?: string
): Promise<PredictionResponse> {
  const params = model ? { model } : {};
  const response = await apiClient.post('/api/v1/predict', data, { params });
  return response.data as PredictionResponse;
}

export async function fetchAllPredictions(
  data: PredictionRequest
): Promise<AllPredictionsResponse> {
  const response = await apiClient.post('/api/v1/predict/all', data);
  return response.data as AllPredictionsResponse;
}

export async function fetchModels(): Promise<ModelInfo[]> {
  const response = await apiClient.get('/api/v1/models');
  return response.data as ModelInfo[];
}
