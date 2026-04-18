// =============================================================================
// SECTION 1 DU FORMULAIRE — Informations sur le bien
//
// Champs : surface, rooms, bathrooms, age, listing_price,
//          market_price_m2, floor, energy_rating, condition, property_type
//
// Ce composant ne gère PAS son propre état — il reçoit `register` et `errors`
// du formulaire parent (PredictionForm). C'est le pattern react-hook-form :
// un seul état centralisé en haut, les sections ne font qu'afficher des inputs.
// =============================================================================

import type { UseFormRegister, FieldErrors } from "react-hook-form";
import type { PredictionRequest } from "../../types";

// -----------------------------------------------------------------------------
// PROPS — ce que le composant reçoit du parent
//
// UseFormRegister<PredictionRequest> : le type exact de la fonction `register`
// fournie par useForm(). Le générique <PredictionRequest> garantit que seuls
// les vrais noms de champs (surface, rooms, etc.) sont acceptés — TypeScript
// refusera "surfaace" par exemple.
// -----------------------------------------------------------------------------
interface Props {
  register: UseFormRegister<PredictionRequest>;
  errors: FieldErrors<PredictionRequest>;
}

// -----------------------------------------------------------------------------
// COMPOSANT UTILITAIRE — champ de formulaire avec label + message d'erreur
//
// On extrait ce petit composant pour éviter de répéter le même markup
// (label + input + message d'erreur) pour chaque champ.
// -----------------------------------------------------------------------------
function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode; // "children" = ce qu'on met entre les balises
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-gray-700">{label}</label>
      {children}
      {/* On affiche le message d'erreur uniquement s'il existe */}
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}

// -----------------------------------------------------------------------------
// SECTION PRINCIPALE
// -----------------------------------------------------------------------------
export function PropertyInfoSection({ register, errors }: Props) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-800 border-b pb-2">
        Informations sur le bien
      </h2>

      {/* Grille 2 colonnes sur écrans moyens et plus */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        {/* --- surface --- */}
        <Field label="Surface (m²)" error={errors.surface?.message}>
          <input
            type="number"
            // register("surface", { validation }) connecte cet input au formulaire.
            // required + min/max sont des règles de validation intégrées.
            {...register("surface", {
              required: "La surface est obligatoire",
              min: { value: 9, message: "Minimum 9 m²" },
              max: { value: 1000, message: "Maximum 1000 m²" },
              valueAsNumber: true, // retourne un number, pas une string
            })}
            placeholder="65"
            defaultValue={65}
            className="input"
          />
        </Field>

        {/* --- rooms --- */}
        <Field label="Nombre de pièces" error={errors.rooms?.message}>
          <input
            type="number"
            {...register("rooms", {
              required: "Obligatoire",
              min: { value: 1, message: "Minimum 1" },
              max: { value: 20, message: "Maximum 20" },
              valueAsNumber: true,
            })}
            placeholder="3"
            defaultValue={3}
            className="input"
          />
        </Field>

        {/* --- bathrooms --- */}
        <Field label="Salles de bain" error={errors.bathrooms?.message}>
          <input
            type="number"
            {...register("bathrooms", {
              required: "Obligatoire",
              min: { value: 1, message: "Minimum 1" },
              max: { value: 10, message: "Maximum 10" },
              valueAsNumber: true,
            })}
            placeholder="1"
            defaultValue={1}
            className="input"
          />
        </Field>

        {/* --- age --- */}
        <Field label="Âge du bien (années)" error={errors.age?.message}>
          <input
            type="number"
            {...register("age", {
              required: "Obligatoire",
              min: { value: 0, message: "Minimum 0" },
              max: { value: 200, message: "Maximum 200" },
              valueAsNumber: true,
            })}
            placeholder="15"
            defaultValue={15}
            className="input"
          />
        </Field>

        {/* --- listing_price --- */}
        <Field label="Prix de vente (€)" error={errors.listing_price?.message}>
          <input
            type="number"
            {...register("listing_price", {
              required: "Obligatoire",
              min: { value: 10000, message: "Minimum 10 000 €" },
              valueAsNumber: true,
            })}
            placeholder="320000"
            defaultValue={320000}
            className="input"
          />
        </Field>

        {/* --- market_price_m2 --- */}
        <Field label="Prix marché au m² (€)" error={errors.market_price_m2?.message}>
          <input
            type="number"
            {...register("market_price_m2", {
              required: "Obligatoire",
              min: { value: 500, message: "Minimum 500 €/m²" },
              valueAsNumber: true,
            })}
            placeholder="4800"
            defaultValue={4800}
            className="input"
          />
        </Field>

        {/* --- floor --- */}
        <Field label="Étage (0 = RDC)" error={errors.floor?.message}>
          <input
            type="number"
            {...register("floor", {
              required: "Obligatoire",
              min: { value: 0, message: "Minimum 0" },
              max: { value: 50, message: "Maximum 50" },
              valueAsNumber: true,
            })}
            placeholder="2"
            defaultValue={2}
            className="input"
          />
        </Field>

        {/* --- property_type --- */}
        <Field label="Type de bien" error={errors.property_type?.message}>
          <select
            {...register("property_type", { required: "Obligatoire" })}
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

        {/* --- energy_rating --- */}
        <Field label="Diagnostic énergétique" error={errors.energy_rating?.message}>
          <select
            {...register("energy_rating", { required: "Obligatoire" })}
            defaultValue="C"
            className="input"
          >
            {/* On génère les options A→G dynamiquement */}
            {["A", "B", "C", "D", "E", "F", "G"].map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </Field>

        {/* --- condition --- */}
        <Field label="État général" error={errors.condition?.message}>
          <select
            {...register("condition", { required: "Obligatoire" })}
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
