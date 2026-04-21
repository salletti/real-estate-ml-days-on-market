import { useState } from 'react';
import { fetchAllPredictions } from '../api/endpoints';
import type { PredictionRequest, PredictionState } from '../types';

export function usePrediction() {
  const [state, setState] = useState<PredictionState>({
    status: 'idle',
    data: null,
    error: null,
  });

  async function predict(formData: PredictionRequest) {
    setState({ status: 'loading', data: null, error: null });

    try {
      const data = await fetchAllPredictions(formData);
      setState({ status: 'success', data, error: null });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur inconnue';
      setState({ status: 'error', data: null, error: message });
    }
  }

  return { state, predict };
}
