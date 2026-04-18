"""
predict.py
----------
Endpoints de prédiction.

Design stateless :
  Le modèle à utiliser est passé en query parameter — pas en état serveur.
  Chaque requête est autonome et indépendante.

Routes :
  POST /api/v1/predict?model=xgboost   → prédiction avec un modèle spécifique
  POST /api/v1/predict/all             → prédictions de tous les modèles
"""

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_model_service
from app.schemas.prediction import (
    AllModelsPredictionResponse,
    PredictionRequest,
    PredictionResponse,
)
from app.services.model_service import ModelService

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict(
    request: PredictionRequest,
    model: str | None = Query(
        default=None,
        description="Nom du modèle à utiliser. Si absent, utilise le meilleur modèle.",
        examples=["xgboost", "random_forest", "linear_regression"],
    ),
    service: ModelService = Depends(get_model_service),
) -> PredictionResponse:
    """
    Prédit le temps de vente d'un bien immobilier.

    Le paramètre `model` est optionnel :
      - POST /api/v1/predict                          → utilise xgboost (défaut)
      - POST /api/v1/predict?model=random_forest      → utilise random_forest
      - POST /api/v1/predict?model=linear_regression  → utilise linear_regression
    """
    result = service.predict(request.model_dump(), model_name=model)
    return PredictionResponse(**result)


@router.post("/predict/all", response_model=AllModelsPredictionResponse)
def predict_all(
    request: PredictionRequest,
    service: ModelService = Depends(get_model_service),
) -> AllModelsPredictionResponse:
    """
    Prédit avec les 3 modèles simultanément.

    Utile pour comparer les résultats côte à côte dans le frontend
    sans faire 3 requêtes séparées.
    """
    results = service.predict_all(request.model_dump())
    return AllModelsPredictionResponse(
        predictions=[PredictionResponse(**r) for r in results]
    )
