// =============================================================================
// TESTS — ModelComparison
//
// Ce composant gère le rendu conditionnel selon PredictionState.status.
// On teste chaque branche : loading, error, success.
//
// Analogie PHPUnit : comme tester un Controller avec différents états de la
// réponse — on vérifie que le bon contenu est rendu selon le contexte.
// =============================================================================

import { render, screen } from '@testing-library/react';
import { ModelComparison } from './ModelComparison';
import type { PredictionState, PredictionResponse } from '../../types';

// -----------------------------------------------------------------------------
// Fixtures — factories pour construire les états de test
// -----------------------------------------------------------------------------

function makePrediction(
  overrides: Partial<PredictionResponse> = {}
): PredictionResponse {
  return {
    model_used: 'xgboost',
    predicted_days: 45,
    lower_bound: 28,
    upper_bound: 62,
    model_metrics: { mae: 15.4, rmse: 19.4, r2: 0.75 },
    ...overrides,
  };
}

const loadingState: PredictionState = { status: 'loading', data: null, error: null };

const errorState: PredictionState = {
  status: 'error',
  data: null,
  error: 'Impossible de contacter le backend',
};

const successState: PredictionState = {
  status: 'success',
  data: {
    predictions: [
      makePrediction({ model_used: 'xgboost', predicted_days: 45 }),
      makePrediction({ model_used: 'random_forest', predicted_days: 52 }),
      makePrediction({ model_used: 'linear_regression', predicted_days: 38 }),
    ],
  },
  error: null,
};

// -----------------------------------------------------------------------------
// Suite de tests
// -----------------------------------------------------------------------------

describe('ModelComparison', () => {
  it("n'affiche rien en état idle", () => {
    const { container } = render(
      <ModelComparison predictionState={{ status: 'idle', data: null, error: null }} />
    );

    // container.firstChild est null quand le composant retourne null
    expect(container.firstChild).toBeNull();
  });

  it('affiche un spinner en état loading', () => {
    render(<ModelComparison predictionState={loadingState} />);

    // Le spinner est un div avec animate-spin — pas de texte, on cherche via la classe
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it("affiche le message d'erreur en état error", () => {
    render(<ModelComparison predictionState={errorState} />);

    expect(screen.getByText('Erreur lors de la prédiction')).toBeInTheDocument();
    expect(screen.getByText('Impossible de contacter le backend')).toBeInTheDocument();
  });

  it('affiche les 3 cartes de résultats en état success', () => {
    render(<ModelComparison predictionState={successState} />);

    // Les 3 noms de modèles formatés doivent être présents
    expect(screen.getByText('Xgboost')).toBeInTheDocument();
    expect(screen.getByText('Random Forest')).toBeInTheDocument();
    expect(screen.getByText('Linear Regression')).toBeInTheDocument();
  });

  it('met en avant le modèle avec le moins de jours prédits', () => {
    render(<ModelComparison predictionState={successState} />);

    // linear_regression a 38 jours → c'est le meilleur → badge "Recommandé"
    // Un seul badge doit être présent
    const badges = screen.getAllByText('Recommandé');
    expect(badges).toHaveLength(1);

    // La carte "Linear Regression" doit contenir le badge
    const linearCard = screen
      .getByText('Linear Regression')
      .closest('div[class*="rounded-xl"]');
    expect(linearCard).toHaveTextContent('Recommandé');
  });

  it("affiche le titre 'Résultats de prédiction' en état success", () => {
    render(<ModelComparison predictionState={successState} />);

    expect(screen.getByText('Résultats de prédiction')).toBeInTheDocument();
  });
});
