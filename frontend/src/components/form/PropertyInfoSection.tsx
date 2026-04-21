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

export function PropertyInfoSection({ register, errors }: Props) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-800 border-b pb-2">
        Informations sur le bien
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Field label="Surface (m²)" error={errors.surface?.message}>
          <input
            type="number"
            {...register('surface', {
              required: 'La surface est obligatoire',
              min: { value: 9, message: 'Minimum 9 m²' },
              max: { value: 1000, message: 'Maximum 1000 m²' },
              valueAsNumber: true,
            })}
            placeholder="65"
            defaultValue={65}
            className="input"
          />
        </Field>

        <Field label="Nombre de pièces" error={errors.rooms?.message}>
          <input
            type="number"
            {...register('rooms', {
              required: 'Obligatoire',
              min: { value: 1, message: 'Minimum 1' },
              max: { value: 20, message: 'Maximum 20' },
              valueAsNumber: true,
            })}
            placeholder="3"
            defaultValue={3}
            className="input"
          />
        </Field>

        <Field label="Salles de bain" error={errors.bathrooms?.message}>
          <input
            type="number"
            {...register('bathrooms', {
              required: 'Obligatoire',
              min: { value: 1, message: 'Minimum 1' },
              max: { value: 10, message: 'Maximum 10' },
              valueAsNumber: true,
            })}
            placeholder="1"
            defaultValue={1}
            className="input"
          />
        </Field>

        <Field label="Âge du bien (années)" error={errors.age?.message}>
          <input
            type="number"
            {...register('age', {
              required: 'Obligatoire',
              min: { value: 0, message: 'Minimum 0' },
              max: { value: 200, message: 'Maximum 200' },
              valueAsNumber: true,
            })}
            placeholder="15"
            defaultValue={15}
            className="input"
          />
        </Field>

        <Field label="Prix de vente (€)" error={errors.listing_price?.message}>
          <input
            type="number"
            {...register('listing_price', {
              required: 'Obligatoire',
              min: { value: 10000, message: 'Minimum 10 000 €' },
              valueAsNumber: true,
            })}
            placeholder="320000"
            defaultValue={320000}
            className="input"
          />
        </Field>

        <Field label="Prix marché au m² (€)" error={errors.market_price_m2?.message}>
          <input
            type="number"
            {...register('market_price_m2', {
              required: 'Obligatoire',
              min: { value: 500, message: 'Minimum 500 €/m²' },
              valueAsNumber: true,
            })}
            placeholder="4800"
            defaultValue={4800}
            className="input"
          />
        </Field>

        <Field label="Étage (0 = RDC)" error={errors.floor?.message}>
          <input
            type="number"
            {...register('floor', {
              required: 'Obligatoire',
              min: { value: 0, message: 'Minimum 0' },
              max: { value: 50, message: 'Maximum 50' },
              valueAsNumber: true,
            })}
            placeholder="2"
            defaultValue={2}
            className="input"
          />
        </Field>

        <Field label="Type de bien" error={errors.property_type?.message}>
          <select
            {...register('property_type', { required: 'Obligatoire' })}
            defaultValue="apartment"
            className="input"
          >
            <option value="apartment">Appartement</option>
            <option value="house">Maison</option>
            <option value="studio">Studio</option>
            <option value="penthouse">Penthouse</option>
            <option value="loft">Loft</option>
          </select>
        </Field>

        <Field label="Diagnostic énergétique" error={errors.energy_rating?.message}>
          <select
            {...register('energy_rating', { required: 'Obligatoire' })}
            defaultValue="C"
            className="input"
          >
            {['A', 'B', 'C', 'D', 'E', 'F', 'G'].map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </Field>

        <Field label="État général" error={errors.condition?.message}>
          <select
            {...register('condition', { required: 'Obligatoire' })}
            defaultValue="good"
            className="input"
          >
            <option value="new">Neuf</option>
            <option value="good">Bon état</option>
            <option value="fair">État moyen</option>
            <option value="poor">Mauvais état</option>
          </select>
        </Field>
      </div>
    </div>
  );
}
