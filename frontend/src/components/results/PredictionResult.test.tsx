// =============================================================================
// TESTS — PredictionResult
//
// Ce composant est purement stateless : on lui donne une PredictionResponse
// et on vérifie qu'il affiche les bonnes informations dans le bon format.
//
// Analogie PHPUnit : comme tester un Helper ou un ValueObject — pas d'état,
// pas de dépendances externes, on contrôle tout via les paramètres.
// =============================================================================

import { render, screen } from '@testing-library/react';
import { PredictionResult } from './PredictionResult';
import type { PredictionResponse } from '../../types';

// -----------------------------------------------------------------------------
// Fixture — données de test réutilisables
// Comme un setUp() en PHPUnit ou une factory Mockery
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

// -----------------------------------------------------------------------------
// Suite de tests
// `describe` regroupe les tests d'un composant — équivalent d'une classe de test
// -----------------------------------------------------------------------------
describe('PredictionResult', () => {
  it('affiche le nombre de jours prédit', () => {
    // render() monte le composant dans un DOM virtuel (jsdom)
    render(<PredictionResult prediction={makePrediction({ predicted_days: 45 })} />);

    // screen.getByText() cherche le texte dans le DOM rendu
    // Comme un assertion sur le HTML généré, mais en plus expressif
    expect(screen.getByText('45')).toBeInTheDocument();
    expect(screen.getByText('jours')).toBeInTheDocument();
  });

  it('affiche le nom du modèle formaté (snake_case → Title Case)', () => {
    render(
      <PredictionResult prediction={makePrediction({ model_used: 'random_forest' })} />
    );

    // "random_forest" doit être transformé en "Random Forest"
    expect(screen.getByText('Random Forest')).toBeInTheDocument();
  });

  it("affiche l'intervalle de confiance arrondi", () => {
    render(
      <PredictionResult
        prediction={makePrediction({ lower_bound: 27.6, upper_bound: 62.4 })}
      />
    );

    // Math.round(27.6) = 28, Math.round(62.4) = 62
    expect(screen.getByText('28 – 62 jours')).toBeInTheDocument();
  });

  // --- Tests de couleur selon le nombre de jours ---
  // getDaysColor() retourne une classe Tailwind selon le seuil.
  // On vérifie la classe CSS présente sur l'élément contenant le chiffre.

  it('affiche en vert pour une vente rapide (≤ 30 jours)', () => {
    render(<PredictionResult prediction={makePrediction({ predicted_days: 25 })} />);

    const daysEl = screen.getByText('25');
    expect(daysEl).toHaveClass('text-green-600');
  });

  it('affiche en orange pour une vente moyenne (31–60 jours)', () => {
    render(<PredictionResult prediction={makePrediction({ predicted_days: 45 })} />);

    const daysEl = screen.getByText('45');
    expect(daysEl).toHaveClass('text-orange-500');
  });

  it('affiche en rouge pour une vente longue (> 60 jours)', () => {
    render(<PredictionResult prediction={makePrediction({ predicted_days: 90 })} />);

    const daysEl = screen.getByText('90');
    expect(daysEl).toHaveClass('text-red-500');
  });

  // --- Tests du flag highlighted ---

  it('affiche le badge "Recommandé" quand highlighted=true', () => {
    render(<PredictionResult prediction={makePrediction()} highlighted={true} />);

    expect(screen.getByText('Recommandé')).toBeInTheDocument();
  });

  it('ne affiche pas le badge "Recommandé" par défaut', () => {
    render(<PredictionResult prediction={makePrediction()} />);

    // queryByText retourne null si l'élément est absent (getByText lancerait une erreur)
    expect(screen.queryByText('Recommandé')).not.toBeInTheDocument();
  });
});
