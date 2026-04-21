import type { UseFormRegister } from 'react-hook-form';
import type { PredictionRequest } from '../../types';

interface Props {
  register: UseFormRegister<PredictionRequest>;
}

function CheckboxField({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="flex items-center gap-3 cursor-pointer select-none">
      {children}
      <span className="text-sm font-medium text-gray-700">{label}</span>
    </label>
  );
}

export function AmenitiesSection({ register }: Props) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-800 border-b pb-2">Aménités</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <CheckboxField label="Balcon">
          <input
            type="checkbox"
            {...register('balcony')}
            defaultChecked={true}
            className="w-4 h-4 rounded accent-blue-600"
          />
        </CheckboxField>

        <CheckboxField label="Terrasse">
          <input
            type="checkbox"
            {...register('terrace')}
            defaultChecked={false}
            className="w-4 h-4 rounded accent-blue-600"
          />
        </CheckboxField>

        <CheckboxField label="Parking">
          <input
            type="checkbox"
            {...register('parking')}
            defaultChecked={true}
            className="w-4 h-4 rounded accent-blue-600"
          />
        </CheckboxField>

        <CheckboxField label="Meublé">
          <input
            type="checkbox"
            {...register('furnished')}
            defaultChecked={false}
            className="w-4 h-4 rounded accent-blue-600"
          />
        </CheckboxField>
      </div>
    </div>
  );
}
