// =============================================================================
// PAGE D'ACCUEIL — HomePage
//
// Assemble le formulaire et les résultats.
// Maintient l'état de prédiction qui circule entre les deux.
//
// Layout :
//   - Header
//   - Sur desktop : formulaire à gauche (40%) | résultats à droite (60%)
//   - Sur mobile  : formulaire en haut, résultats en bas
// =============================================================================

import { useState } from "react";
import { PredictionForm } from "../components/form/PredictionForm";
import { ModelComparison } from "../components/results/ModelComparison";
import { ModelExplainer } from "../components/ModelExplainer";
import type { PredictionState } from "../types";

export function HomePage() {
  // ---------------------------------------------------------------------------
  // État de prédiction — vit ici car utilisé par deux composants enfants :
  //   - PredictionForm  le met à jour (via onPrediction callback)
  //   - ModelComparison le lit pour afficher les résultats
  //
  // C'est le pattern "lift state up" : quand deux composants ont besoin
  // du même état, on le fait remonter à leur ancêtre commun.
  // ---------------------------------------------------------------------------
  const [predictionState, setPredictionState] = useState<PredictionState>({
    status: "idle",
    data: null,
    error: null,
  });

  return (
    <div className="min-h-screen bg-gray-50">

      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900">
            Days on Market
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Estimez le temps de vente de votre bien immobilier
          </p>
        </div>
      </header>

      {/* Contenu principal */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {/*
          Layout deux colonnes sur desktop, une colonne sur mobile.
          `items-start` évite que la colonne de droite s'étire
          pour occuper toute la hauteur de la colonne de gauche.
        */}
        <div className="flex flex-col md:flex-row gap-8 items-start">

          {/* Colonne gauche — Formulaire */}
          <div className="w-full md:w-2/5 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <PredictionForm onPrediction={setPredictionState} />
          </div>

          {/* Colonne droite — Résultats */}
          <div className="w-full md:w-3/5">
            {/* État idle : message d'invitation */}
            {predictionState.status === "idle" && (
              <div className="flex flex-col items-center justify-center py-20 text-center text-gray-400">
                <p className="text-5xl mb-4">🏠</p>
                <p className="text-lg font-medium">Remplissez le formulaire</p>
                <p className="text-sm mt-1">
                  Les prédictions des 3 modèles s'afficheront ici
                </p>
              </div>
            )}

            {/* Tous les autres états sont gérés par ModelComparison */}
            {predictionState.status !== "idle" && (
              <ModelComparison predictionState={predictionState} />
            )}
          </div>

        </div>

        {/* Section pédagogique — toujours visible, sous les résultats */}
        <ModelExplainer />
      </main>
    </div>
  );
}
