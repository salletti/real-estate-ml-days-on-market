// =============================================================================
// COMPARAISON DES MODÈLES — ModelComparison
//
// Reçoit le PredictionState complet et affiche le bon contenu selon le statut :
//   idle    → rien (zone vide)
//   loading → spinner
//   error   → message d'erreur (déjà géré dans PredictionForm, ici en backup)
//   success → 3 cartes PredictionResult côte à côte
// =============================================================================

import { PredictionResult } from './PredictionResult';
import type { PredictionState } from '../../types';

interface Props {
  predictionState: PredictionState;
}

export function ModelComparison({ predictionState }: Props) {
  const { status, data } = predictionState;

  // --- idle : l'utilisateur n'a pas encore soumis ---
  if (status === 'idle') return null;

  // --- loading : spinner centré ---
  if (status === 'loading') {
    return (
      <div className="flex justify-center items-center py-16">
        {/*
          Spinner CSS pur via Tailwind :
          - `animate-spin` tourne l'élément en continu
          - `border-t-blue-600` colore UN seul côté → effet de roue qui tourne
          - `border-gray-200` colore les 3 autres côtés en gris clair
        */}
        <div className="w-10 h-10 rounded-full border-4 border-gray-200 border-t-blue-600 animate-spin" />
      </div>
    );
  }

  // --- error : message lisible ---
  if (status === 'error') {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-center">
        <p className="text-red-600 font-medium">Erreur lors de la prédiction</p>
        <p className="text-red-400 text-sm mt-1">{predictionState.error}</p>
      </div>
    );
  }

  // --- success : on a les données ---
  // TypeScript sait ici que data n'est pas null (on a vérifié status === "success")
  // mais on garde le guard `if (!data)` pour être safe
  if (!data || data.predictions.length === 0) return null;

  // -------------------------------------------------------------------------
  // Déterminer le modèle "recommandé" = celui avec le moins de jours prédits
  //
  // Math.min(...array) retourne le plus petit nombre d'un tableau.
  // On l'utilise pour trouver la valeur minimale, puis on retrouve l'index
  // du modèle correspondant.
  // -------------------------------------------------------------------------
  const minDays = Math.min(...data.predictions.map((p) => p.predicted_days));
  const bestIndex = data.predictions.findIndex((p) => p.predicted_days === minDays);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-800 text-center">
        Résultats de prédiction
      </h2>

      {/* Grille responsive : 1 colonne mobile, 3 colonnes desktop */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {data.predictions.map((prediction, index) => (
          <PredictionResult
            key={prediction.model_used}
            prediction={prediction}
            // Le modèle avec le moins de jours reçoit highlighted=true
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
