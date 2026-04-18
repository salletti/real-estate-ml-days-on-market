"""
prediction.py (schemas)
-----------------------
Définit la forme des données qui entrent et sortent de l'endpoint /predict.

Pydantic valide automatiquement chaque champ à la réception de la requête :
  - type incorrect → HTTP 422 avec message d'erreur clair
  - champ manquant → HTTP 422
  - valeur hors Literal → HTTP 422

Cela évite d'écrire des validations manuelles dans les routes.
"""

from typing import Any, Literal

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """
    Les 17 features d'un bien immobilier.
    Mirrors exactement FEATURE_COLUMNS dans constants.py.
    """

    # Features numériques
    surface: float = Field(..., gt=0, description="Surface en m²")
    rooms: int = Field(..., ge=1, le=20)
    bathrooms: int = Field(..., ge=1, le=10)
    age: int = Field(..., ge=0, le=200)
    listing_price: float = Field(..., gt=0, description="Prix demandé en €")
    market_price_m2: float = Field(..., gt=0, description="Prix du marché en €/m²")
    floor: int = Field(..., ge=0, le=50)

    # Features ordinales
    energy_rating: Literal["A", "B", "C", "D", "E", "F", "G"]
    condition: Literal["new", "good", "fair", "poor"]

    # Features catégorielles
    property_type: Literal["apartment", "house", "studio", "penthouse", "loft"]
    city: str = Field(..., min_length=1)
    neighborhood: str = Field(..., min_length=1)
    zipcode: str = Field(..., min_length=4)

    # Features binaires
    balcony: bool
    terrace: bool
    parking: bool
    furnished: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "surface": 75.0,
                "rooms": 3,
                "bathrooms": 1,
                "age": 15,
                "listing_price": 320000,
                "market_price_m2": 4200,
                "floor": 2,
                "energy_rating": "C",
                "condition": "good",
                "property_type": "apartment",
                "city": "Paris",
                "neighborhood": "Marais",
                "zipcode": "75003",
                "balcony": True,
                "terrace": False,
                "parking": False,
                "furnished": False,
            }
        }
    }


class PredictionResponse(BaseModel):
    """Résultat d'une prédiction."""

    predicted_days: int
    lower_bound: int  # borne basse de l'intervalle de confiance à 95%
    upper_bound: int  # borne haute de l'intervalle de confiance à 95%
    model_used: str
    model_metrics: dict[str, Any]  # mae, rmse, r2


class AllModelsPredictionResponse(BaseModel):
    """Résultats de tous les modèles pour une même requête."""

    predictions: list[PredictionResponse]
