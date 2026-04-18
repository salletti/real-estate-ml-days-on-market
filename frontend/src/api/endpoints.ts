// =============================================================================
// API ENDPOINTS — Fonctions d'appel HTTP
// =============================================================================

import apiClient from './client';
import type {
  PredictionRequest,
  PredictionResponse,
  AllPredictionsResponse,
  ModelInfo,
} from '../types';

// -----------------------------------------------------------------------------
// POST /api/v1/predict?model=xgboost
//
// Prédiction avec UN seul modèle. `model` est optionnel (défaut = xgboost).
// Le `?` dans `model?: string` rend l'argument facultatif côté TypeScript.
// -----------------------------------------------------------------------------
export async function fetchPrediction(
  data: PredictionRequest,
  model?: string
): Promise<PredictionResponse> {
  const params = model ? { model } : {};

  const response = await apiClient.post('/api/v1/predict', data, { params });
  return response.data as PredictionResponse;
}

// -----------------------------------------------------------------------------
// POST /api/v1/predict/all
//
// Prédictions des 3 modèles en une seule requête.
// -----------------------------------------------------------------------------
export async function fetchAllPredictions(
  data: PredictionRequest
): Promise<AllPredictionsResponse> {
  const response = await apiClient.post('/api/v1/predict/all', data);
  return response.data as AllPredictionsResponse;
}

// -----------------------------------------------------------------------------
// GET /api/v1/models
//
// Liste des 3 modèles avec leurs métriques (MAE, RMSE, R²).
// -----------------------------------------------------------------------------
export async function fetchModels(): Promise<ModelInfo[]> {
  const response = await apiClient.get('/api/v1/models');
  return response.data as ModelInfo[];
}
