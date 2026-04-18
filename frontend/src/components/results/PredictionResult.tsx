// =============================================================================
// RÉSULTAT D'UN MODÈLE — PredictionResult
//
// Composant purement visuel (pas d'état, pas d'appel API).
// Reçoit un PredictionResponse et l'affiche sous forme de carte.
//
// Affiché 3 fois côte à côte dans ModelComparison (une carte par modèle).
// =============================================================================

import type { PredictionResponse } from "../../types";

interface Props {
  prediction: PredictionResponse;
  // `highlighted` marque la meilleure prédiction (la plus rapide)
  highlighted?: boolean;
}

// -----------------------------------------------------------------------------
// Formate le nom technique du modèle en libellé lisible
// "random_forest" → "Random Forest"
// -----------------------------------------------------------------------------
function formatModelName(name: string): string {
  return name
    .split("_")                          // ["random", "forest"]
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1)) // ["Random", "Forest"]
    .join(" ");                          // "Random Forest"
}

// -----------------------------------------------------------------------------
// Retourne une couleur Tailwind selon le nombre de jours prédit
// Vert = vente rapide, orange = moyen, rouge = long
// -----------------------------------------------------------------------------
function getDaysColor(days: number): string {
  if (days <= 30)  return "text-green-600";
  if (days <= 60)  return "text-orange-500";
  return "text-red-500";
}

export function PredictionResult({ prediction, highlighted = false }: Props) {
  const { model_used, predicted_days, lower_bound, upper_bound } = prediction;

  return (
    <div
      className={`
        rounded-xl border p-5 flex flex-col gap-3 transition-shadow
        ${highlighted
          ? "border-blue-500 shadow-lg shadow-blue-100 bg-blue-50"
          : "border-gray-200 bg-white shadow-sm"
        }
      `}
    >
      {/* En-tête : nom du modèle + badge "Recommandé" si highlighted */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-800">
          {formatModelName(model_used)}
        </h3>
        {highlighted && (
          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-600 text-white">
            Recommandé
          </span>
        )}
      </div>

      {/* Prédiction centrale — le chiffre principal */}
      <div className="text-center py-2">
        <span className={`text-4xl font-bold ${getDaysColor(predicted_days)}`}>
          {predicted_days}
        </span>
        <span className="text-gray-500 text-sm ml-2">jours</span>
      </div>

      {/* Intervalle de confiance à 95% */}
      <div className="bg-gray-50 rounded-lg p-3 text-center">
        <p className="text-xs text-gray-500 mb-1">Intervalle de confiance 95%</p>
        <p className="text-sm font-medium text-gray-700">
          {/* Math.round arrondit à l'entier le plus proche */}
          {Math.round(lower_bound)} – {Math.round(upper_bound)} jours
        </p>
      </div>
    </div>
  );
}
