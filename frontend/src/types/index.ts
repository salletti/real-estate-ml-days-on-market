export interface PredictionRequest {
  surface: number;
  rooms: number;
  bathrooms: number;
  age: number;
  listing_price: number;
  market_price_m2: number;
  floor: number;
  energy_rating: 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G';
  condition: 'new' | 'good' | 'fair' | 'poor';
  property_type: 'apartment' | 'house' | 'studio' | 'penthouse' | 'loft';
  city: string;
  neighborhood: string;
  zipcode: string;
  balcony: boolean;
  terrace: boolean;
  parking: boolean;
  furnished: boolean;
}

export interface PredictionResponse {
  model_used: string;
  predicted_days: number;
  lower_bound: number;
  upper_bound: number;
  model_metrics: {
    mae: number;
    rmse: number;
    r2: number;
  };
}

export interface AllPredictionsResponse {
  predictions: PredictionResponse[];
}

export interface ModelInfo {
  name: string;
  mae: number;
  rmse: number;
  r2: number;
}

export type ApiStatus = 'idle' | 'loading' | 'success' | 'error';

export interface PredictionState {
  status: ApiStatus;
  data: AllPredictionsResponse | null;
  error: string | null;
}
