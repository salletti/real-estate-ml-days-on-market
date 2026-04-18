// =============================================================================
// FORMULAIRE PRINCIPAL — PredictionForm
// =============================================================================

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { usePrediction } from '../../hooks/usePrediction';
import { PropertyInfoSection } from './PropertyInfoSection';
import { LocationSection } from './LocationSection';
import { AmenitiesSection } from './AmenitiesSection';
import type { PredictionRequest, PredictionState } from '../../types';

interface Props {
  onPrediction: (state: PredictionState) => void;
}

export function PredictionForm({ onPrediction }: Props) {
  // Le backend accepte des booléens natifs pour les checkboxes —
  // PredictionRequest est maintenant directement compatible avec le formulaire.
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PredictionRequest>();

  const { state, predict } = usePrediction();

  useEffect(() => {
    onPrediction(state);
  }, [state]); // eslint-disable-line react-hooks/exhaustive-deps

  async function onSubmit(data: PredictionRequest) {
    await predict(data);
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
      <PropertyInfoSection register={register} errors={errors} />
      <LocationSection register={register} errors={errors} />
      <AmenitiesSection register={register} />

      <button
        type="submit"
        disabled={state.status === 'loading'}
        className="w-full py-3 px-6 bg-blue-600 text-white font-semibold rounded-lg
                   hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed
                   transition-colors duration-200"
      >
        {state.status === 'loading'
          ? 'Calcul en cours...'
          : 'Prédire le temps de vente'}
      </button>

      {state.status === 'error' && (
        <p className="text-sm text-red-500 text-center">{state.error}</p>
      )}
    </form>
  );
}
