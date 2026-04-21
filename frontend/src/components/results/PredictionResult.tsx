import type { PredictionResponse } from '../../types';

interface Props {
  prediction: PredictionResponse;
  highlighted?: boolean;
}

function formatModelName(name: string): string {
  return name
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

function getDaysColor(days: number): string {
  if (days <= 30) return 'text-green-600';
  if (days <= 60) return 'text-orange-500';
  return 'text-red-500';
}

export function PredictionResult({ prediction, highlighted = false }: Props) {
  const { model_used, predicted_days, lower_bound, upper_bound } = prediction;

  return (
    <div
      className={`
        rounded-xl border p-5 flex flex-col gap-3 transition-shadow
        ${
          highlighted
            ? 'border-blue-500 shadow-lg shadow-blue-100 bg-blue-50'
            : 'border-gray-200 bg-white shadow-sm'
        }
      `}
    >
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-800">{formatModelName(model_used)}</h3>
        {highlighted && (
          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-600 text-white">
            Recommandé
          </span>
        )}
      </div>

      <div className="text-center py-2">
        <span className={`text-4xl font-bold ${getDaysColor(predicted_days)}`}>
          {predicted_days}
        </span>
        <span className="text-gray-500 text-sm ml-2">jours</span>
      </div>

      <div className="bg-gray-50 rounded-lg p-3 text-center">
        <p className="text-xs text-gray-500 mb-1">Intervalle de confiance 95%</p>
        <p className="text-sm font-medium text-gray-700">
          {Math.round(lower_bound)} – {Math.round(upper_bound)} jours
        </p>
      </div>
    </div>
  );
}
