import { PredictionResult } from './PredictionResult';
import type { PredictionState } from '../../types';

interface Props {
  predictionState: PredictionState;
}

export function ModelComparison({ predictionState }: Props) {
  const { status, data } = predictionState;

  if (status === 'idle') return null;

  if (status === 'loading') {
    return (
      <div className="flex justify-center items-center py-16">
        <div className="w-10 h-10 rounded-full border-4 border-gray-200 border-t-blue-600 animate-spin" />
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-center">
        <p className="text-red-600 font-medium">Erreur lors de la prédiction</p>
        <p className="text-red-400 text-sm mt-1">{predictionState.error}</p>
      </div>
    );
  }

  if (!data || data.predictions.length === 0) return null;

  const minDays = Math.min(...data.predictions.map((p) => p.predicted_days));
  const bestIndex = data.predictions.findIndex((p) => p.predicted_days === minDays);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-800 text-center">
        Résultats de prédiction
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {data.predictions.map((prediction, index) => (
          <PredictionResult
            key={prediction.model_used}
            prediction={prediction}
            highlighted={index === bestIndex}
          />
        ))}
      </div>

      <p className="text-xs text-gray-400 text-center">
        Intervalles de confiance à 95% · Modèles entraînés sur données simulées
      </p>
    </div>
  );
}
