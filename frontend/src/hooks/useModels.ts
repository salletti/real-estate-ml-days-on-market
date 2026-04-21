import { useState, useEffect } from 'react';
import { fetchModels } from '../api/endpoints';
import type { ModelInfo, ApiStatus } from '../types';

export function useModels() {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [status, setStatus] = useState<ApiStatus>('loading');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchModels()
      .then((data) => {
        setModels(data);
        setStatus('success');
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Erreur inconnue');
        setStatus('error');
      });
  }, []);

  return { models, status, error };
}
