// =============================================================================
// MODEL EXPLAINER — Section pédagogique sous les résultats
//
// Explique les 3 algorithmes, les 3 métriques, et le choix de cette combinaison.
// Composant purement statique : pas de props, pas d'état, pas d'appel API.
// =============================================================================

// -----------------------------------------------------------------------------
// Données statiques — définition des 3 modèles
// -----------------------------------------------------------------------------
const MODELS = [
  {
    name: "Régression Linéaire",
    tag: "Baseline",
    tagColor: "bg-gray-100 text-gray-600",
    description:
      "Le modèle le plus simple : il cherche une relation linéaire directe entre les features et le nombre de jours.",
    formula: "jours = a×surface + b×prix + c×état + … + constante",
    strength: "Rapide, interprétable, excellent point de comparaison.",
    weakness: "Ne capture pas les interactions entre features (ex : l'effet du prix dépend de l'état du bien).",
    insight:
      "Après ajout de la feature price_ratio, la régression linéaire atteint le même R² qu'XGBoost (0.89). Preuve qu'un bon feature engineering bat souvent un modèle plus complexe.",
  },
  {
    name: "Random Forest",
    tag: "Robuste",
    tagColor: "bg-green-100 text-green-700",
    description:
      "200 arbres de décision entraînés en parallèle sur des sous-ensembles aléatoires des données. La prédiction finale est la moyenne des 200 résultats.",
    formula: "prédiction = moyenne(arbre₁, arbre₂, …, arbre₂₀₀)",
    strength: "Robuste au bruit, peu sensible au surapprentissage. Intervalle de confiance naturel via la dispersion des arbres.",
    weakness: "Modèle plus lourd qu'XGBoost, légèrement moins précis sur données tabulaires.",
    insight:
      "Si les 200 arbres divergent sur un bien → intervalle large (incertitude élevée). S'ils convergent → intervalle étroit (prédiction fiable).",
  },
  {
    name: "XGBoost",
    tag: "Recommandé",
    tagColor: "bg-blue-100 text-blue-700",
    description:
      "Les arbres sont construits séquentiellement : chaque nouvel arbre corrige les erreurs résiduelles du précédent (gradient boosting).",
    formula: "prédiction = arbre₁ + correction₂ + correction₃ + …",
    strength: "Très précis sur les données tabulaires. Référence dans les compétitions de ML (Kaggle).",
    weakness: "Plus sensible au surapprentissage, nécessite un tuning des hyperparamètres.",
    insight:
      "Différence clé avec Random Forest : les arbres sont dépendants (chacun corrige le précédent) au lieu d'être indépendants.",
  },
];

// -----------------------------------------------------------------------------
// Données statiques — définition des 3 métriques
// -----------------------------------------------------------------------------
const METRICS = [
  {
    name: "MAE",
    full: "Mean Absolute Error",
    formula: "moyenne(|jours_réels − jours_prédits|)",
    description:
      "Erreur moyenne en jours. La métrique la plus lisible : un MAE de 10 signifie que le modèle se trompe en moyenne de 10 jours.",
    color: "border-l-blue-400",
  },
  {
    name: "RMSE",
    full: "Root Mean Squared Error",
    formula: "√ moyenne((jours_réels − jours_prédits)²)",
    description:
      "Similaire au MAE, mais pénalise davantage les grosses erreurs. Utile pour détecter si le modèle se trompe très fort sur quelques cas.",
    color: "border-l-purple-400",
  },
  {
    name: "R²",
    full: "Coefficient de détermination",
    formula: "1 − (variance résiduelle / variance totale)",
    description:
      "Proportion de la variabilité expliquée par le modèle. R²=0.89 signifie que le modèle explique 89% des variations de temps de vente.",
    color: "border-l-green-400",
  },
];

// -----------------------------------------------------------------------------
// COMPOSANT PRINCIPAL
// -----------------------------------------------------------------------------
export function ModelExplainer() {
  return (
    <div className="space-y-10 mt-10 border-t border-gray-200 pt-10">

      {/* Titre de section */}
      <div className="text-center">
        <h2 className="text-xl font-bold text-gray-800">Comprendre les modèles</h2>
        <p className="text-sm text-gray-500 mt-1">
          Pourquoi trois algorithmes différents, et comment lire leurs performances
        </p>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* SECTION 1 — Les 3 algorithmes                                       */}
      {/* ------------------------------------------------------------------ */}
      <div>
        <h3 className="text-base font-semibold text-gray-700 mb-4">Les 3 algorithmes</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {MODELS.map((model) => (
            <div
              key={model.name}
              className="bg-white border border-gray-200 rounded-xl p-5 space-y-3 shadow-sm"
            >
              {/* En-tête */}
              <div className="flex items-start justify-between gap-2">
                <h4 className="font-semibold text-gray-800 text-sm">{model.name}</h4>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full shrink-0 ${model.tagColor}`}>
                  {model.tag}
                </span>
              </div>

              {/* Description */}
              <p className="text-sm text-gray-600">{model.description}</p>

              {/* Formule */}
              <div className="bg-gray-50 rounded-lg px-3 py-2">
                <p className="text-xs font-mono text-gray-500">{model.formula}</p>
              </div>

              {/* Forces / Faiblesses */}
              <div className="space-y-1 text-xs">
                <p className="text-green-700">
                  <span className="font-medium">Force : </span>{model.strength}
                </p>
                <p className="text-red-600">
                  <span className="font-medium">Limite : </span>{model.weakness}
                </p>
              </div>

              {/* Insight */}
              <div className="border-t border-gray-100 pt-2">
                <p className="text-xs text-gray-400 italic">{model.insight}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* SECTION 2 — Pourquoi ces trois ?                                    */}
      {/* ------------------------------------------------------------------ */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-5">
        <h3 className="text-base font-semibold text-gray-700 mb-2">
          Pourquoi ces trois modèles ensemble ?
        </h3>
        <p className="text-sm text-gray-600">
          Comparer des modèles de complexité croissante est une bonne pratique ML :
        </p>
        <ul className="mt-3 space-y-2 text-sm text-gray-600">
          <li className="flex gap-2">
            <span className="font-semibold text-gray-700 shrink-0">1. Baseline simple</span>
            — La régression linéaire fixe un plancher de performance. Si XGBoost ne fait pas mieux, le problème ou les données ont un problème.
          </li>
          <li className="flex gap-2">
            <span className="font-semibold text-gray-700 shrink-0">2. Modèle robuste</span>
            — Random Forest introduit la non-linéarité et offre un intervalle de confiance natif via la dispersion de ses 200 arbres.
          </li>
          <li className="flex gap-2">
            <span className="font-semibold text-gray-700 shrink-0">3. Modèle de référence</span>
            — XGBoost est l'état de l'art sur les données tabulaires. Son score donne la limite supérieure réaliste pour ce type de problème.
          </li>
        </ul>
        <p className="text-xs text-gray-400 mt-3">
          Si les trois modèles convergent vers une valeur similaire → la prédiction est fiable.
          Si ils divergent → le bien est atypique ou les données sont insuffisantes.
        </p>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* SECTION 3 — Les métriques                                           */}
      {/* ------------------------------------------------------------------ */}
      <div>
        <h3 className="text-base font-semibold text-gray-700 mb-4">Les métriques d'évaluation</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {METRICS.map((metric) => (
            <div
              key={metric.name}
              className={`bg-white border border-gray-200 border-l-4 rounded-xl p-5 space-y-2 shadow-sm ${metric.color}`}
            >
              <div>
                <span className="text-lg font-bold text-gray-800">{metric.name}</span>
                <span className="text-xs text-gray-400 ml-2">{metric.full}</span>
              </div>

              {/* Formule */}
              <div className="bg-gray-50 rounded px-3 py-1.5">
                <p className="text-xs font-mono text-gray-500">{metric.formula}</p>
              </div>

              <p className="text-sm text-gray-600">{metric.description}</p>
            </div>
          ))}
        </div>

        {/* Tableau des résultats obtenus */}
        <div className="mt-4 bg-gray-900 rounded-xl p-4 overflow-x-auto">
          <p className="text-xs text-gray-400 mb-3 font-mono">// Résultats obtenus sur le test set</p>
          <table className="w-full text-sm font-mono">
            <thead>
              <tr className="text-gray-400 text-xs">
                <th className="text-left pb-2">Modèle</th>
                <th className="text-right pb-2">MAE</th>
                <th className="text-right pb-2">RMSE</th>
                <th className="text-right pb-2">R²</th>
              </tr>
            </thead>
            <tbody className="text-gray-200">
              <tr>
                <td className="py-1">linear_regression</td>
                <td className="text-right">10.06</td>
                <td className="text-right">12.91</td>
                <td className="text-right text-green-400">0.89</td>
              </tr>
              <tr>
                <td className="py-1">random_forest</td>
                <td className="text-right">10.92</td>
                <td className="text-right">13.80</td>
                <td className="text-right text-yellow-400">0.87</td>
              </tr>
              <tr className="border-t border-gray-700">
                <td className="py-1 text-blue-400 font-semibold">xgboost ★</td>
                <td className="text-right text-blue-300">9.97</td>
                <td className="text-right text-blue-300">12.78</td>
                <td className="text-right text-blue-300">0.89</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
