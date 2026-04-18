// =============================================================================
// HOOK usePrediction
//
// Encapsule l'appel à POST /api/v1/predict/all et gère les états :
//   idle → loading → success | error
//
// Les composants qui utilisent ce hook reçoivent :
//   - `state`   : les données, le statut, et l'éventuelle erreur
//   - `predict` : la fonction à appeler quand l'utilisateur soumet le formulaire
// =============================================================================

import { useState } from 'react';
import { fetchAllPredictions } from '../api/endpoints';
import type { PredictionRequest, PredictionState } from '../types';

// -----------------------------------------------------------------------------
// useState — mémoire locale d'un composant (ou d'un hook)
//
// useState<T>(valeurInitiale) retourne un tableau de deux éléments :
//   [valeurActuelle, fonctionPourLaModifier]
//
// À chaque appel de la fonction de modification, React re-rend le composant
// avec la nouvelle valeur. C'est le mécanisme central de React.
// -----------------------------------------------------------------------------

export function usePrediction() {
  // On utilise PredictionState (défini dans types/index.ts) comme type de l'état.
  // Valeur initiale : pas encore de requête, pas de données, pas d'erreur.
  const [state, setState] = useState<PredictionState>({
    status: 'idle',
    data: null,
    error: null,
  });

  // ---------------------------------------------------------------------------
  // predict — fonction exposée aux composants
  //
  // Elle est `async` car fetchAllPredictions retourne une Promise.
  // On utilise try/catch pour capturer les erreurs réseau ou HTTP.
  // ---------------------------------------------------------------------------
  async function predict(formData: PredictionRequest) {
    // 1. On passe en mode "chargement" — l'UI peut afficher un spinner
    setState({ status: 'loading', data: null, error: null });

    try {
      // 2. Appel API — on attend la réponse du backend
      const data = await fetchAllPredictions(formData);

      // 3. Succès — on stocke les résultats
      setState({ status: 'success', data, error: null });
    } catch (err) {
      // 4. Erreur — on extrait un message lisible
      //
      // `err` est typé `unknown` en TypeScript strict : on ne sait pas
      // à l'avance si c'est une Error, une string, ou autre chose.
      // On vérifie donc avec `instanceof Error` avant d'accéder à `.message`.
      const message = err instanceof Error ? err.message : 'Erreur inconnue';

      setState({ status: 'error', data: null, error: message });
    }
  }

  // On retourne les deux éléments dont les composants ont besoin
  return { state, predict };
}
