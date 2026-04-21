import type { UseFormRegister, FieldErrors } from 'react-hook-form';
import type { PredictionRequest } from '../../types';

interface Props {
  register: UseFormRegister<PredictionRequest>;
  errors: FieldErrors<PredictionRequest>;
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-gray-700">{label}</label>
      {children}
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}

export function LocationSection({ register, errors }: Props) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-800 border-b pb-2">
        Localisation
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Field label="Ville" error={errors.city?.message}>
          <input
            type="text"
            {...register('city', {
              required: 'La ville est obligatoire',
              minLength: { value: 2, message: 'Minimum 2 caractères' },
              maxLength: { value: 100, message: 'Maximum 100 caractères' },
            })}
            placeholder="Paris"
            defaultValue="Paris"
            className="input"
          />
        </Field>

        <Field label="Quartier" error={errors.neighborhood?.message}>
          <input
            type="text"
            {...register('neighborhood', {
              required: 'Le quartier est obligatoire',
              minLength: { value: 2, message: 'Minimum 2 caractères' },
              maxLength: { value: 100, message: 'Maximum 100 caractères' },
            })}
            placeholder="Montmartre"
            defaultValue="Montmartre"
            className="input"
          />
        </Field>

        <Field label="Code postal" error={errors.zipcode?.message}>
          <input
            type="text"
            {...register('zipcode', {
              required: 'Le code postal est obligatoire',
              pattern: { value: /^\d{5}$/, message: 'Format invalide (ex: 75018)' },
            })}
            placeholder="75018"
            defaultValue="75018"
            className="input"
          />
        </Field>
      </div>
    </div>
  );
}
