// =============================================================================
// TYPES FRONTEND — days-on-market
//
// Ce fichier est le "contrat de données" entre le frontend et le backend.
// Chaque interface ici correspond exactement à ce que le backend envoie ou attend.
// TypeScript vérifie que le code respecte ce contrat au moment de la compilation.
// =============================================================================

// -----------------------------------------------------------------------------
// 1. REQUÊTE — ce qu'on ENVOIE au backend (POST /api/v1/predict)
// -----------------------------------------------------------------------------
// Correspond à PredictionRequest dans backend/app/schemas/prediction.py
// Les 17 features du formulaire. price_ratio est calculé côté backend.

export interface PredictionRequest {
  // --- Numériques ---
  surface: number; // Surface en m²
  rooms: number; // Nombre de pièces
  bathrooms: number; // Nombre de salles de bain
  age: number; // Âge du bien en années
  listing_price: number; // Prix demandé en euros
  market_price_m2: number; // Prix moyen du marché au m² dans la zone
  floor: number; // Étage (0 = rez-de-chaussée)

  // --- Ordinaux (valeurs fixes imposées par le backend) ---
  energy_rating: 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G'; // Diagnostic énergétique
  condition: 'new' | 'good' | 'fair' | 'poor'; // État général du bien

  // --- Catégoriels ---
  property_type: 'apartment' | 'house' | 'studio' | 'penthouse' | 'loft';
  city: string; // Ex: "Paris", "Lyon"
  neighborhood: string; // Ex: "Montmartre", "Croix-Rousse"
  zipcode: string; // Ex: "75018"

  // --- Binaires ---
  // Le backend Pydantic attend des booléens natifs (bool Python = true/false JSON)
  balcony: boolean;
  terrace: boolean;
  parking: boolean;
  furnished: boolean;
}

// -----------------------------------------------------------------------------
// 2. RÉPONSE D'UN SEUL MODÈLE — ce qu'on REÇOIT du backend
// -----------------------------------------------------------------------------
// Correspond à PredictionResponse dans backend/app/schemas/prediction.py

export interface PredictionResponse {
  model_used: string; // Nom du modèle : "xgboost", "random_forest", etc.
  predicted_days: number; // Prédiction centrale (jours avant vente)
  lower_bound: number; // Borne basse de l'intervalle de confiance à 95%
  upper_bound: number; // Borne haute de l'intervalle de confiance à 95%
  model_metrics: {
    // Métriques du modèle
    mae: number;
    rmse: number;
    r2: number;
  };
}

// -----------------------------------------------------------------------------
// 3. RÉPONSE POUR TOUS LES MODÈLES — endpoint /predict/all
// -----------------------------------------------------------------------------
// Le backend renvoie un objet avec les 3 prédictions dans un tableau

export interface AllPredictionsResponse {
  predictions: PredictionResponse[]; // Tableau de 3 PredictionResponse
}

// -----------------------------------------------------------------------------
// 4. INFO D'UN MODÈLE — endpoint GET /api/v1/models
// -----------------------------------------------------------------------------
// Correspond à ModelInfo dans backend/app/schemas/model_info.py

export interface ModelInfo {
  name: string; // Identifiant : "xgboost", "random_forest", "linear_regression"
  mae: number; // Mean Absolute Error — erreur moyenne en jours
  rmse: number; // Root Mean Squared Error — erreur quadratique moyenne
  r2: number; // R² — coefficient de détermination (0 à 1, plus c'est haut mieux c'est)
}

// -----------------------------------------------------------------------------
// 5. ÉTAT DE L'UI — types utilitaires pour gérer le chargement et les erreurs
// -----------------------------------------------------------------------------
// Ces types ne viennent pas du backend. Ils servent à modéliser l'état interne
// des composants et des hooks React.

// Représente l'état générique d'un appel API asynchrone
export type ApiStatus = 'idle' | 'loading' | 'success' | 'error';
// - idle    : l'utilisateur n'a pas encore soumis
// - loading : la requête est en cours
// - success : la réponse est arrivée sans erreur
// - error   : quelque chose a mal tourné

// Regroupe l'état complet d'une prédiction dans un seul objet
export interface PredictionState {
  status: ApiStatus;
  data: AllPredictionsResponse | null; // null tant qu'on n'a pas de résultat
  error: string | null; // message d'erreur lisible
}
