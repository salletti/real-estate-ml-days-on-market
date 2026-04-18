// =============================================================================
// HOOK useModels
//
// Charge automatiquement la liste des modèles ML au montage du composant.
// Contrairement à usePrediction (déclenché par l'utilisateur), ce hook
// démarre tout seul dès que le composant apparaît à l'écran.
// =============================================================================

import { useState, useEffect } from 'react';
import { fetchModels } from '../api/endpoints';
import type { ModelInfo, ApiStatus } from '../types';

export function useModels() {
  // Trois états indépendants : les données, le statut, l'erreur
  // On part en "loading" directement car on sait qu'on va charger tout de suite
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [status, setStatus] = useState<ApiStatus>('loading');
  const [error, setError] = useState<string | null>(null);

  // ---------------------------------------------------------------------------
  // useEffect — exécuté APRÈS le premier rendu du composant
  //
  // C'est l'équivalent React de "quand le composant est prêt, fais ça".
  // Le tableau vide `[]` en second argument est crucial : il dit à React
  // "exécute cet effet UNE SEULE FOIS au montage". Sans lui, l'effet
  // s'exécuterait après chaque re-rendu → boucle infinie de requêtes.
  // ---------------------------------------------------------------------------
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
  }, []); // [] = dépendances vides = montage uniquement

  return { models, status, error };
}
