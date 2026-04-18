"""
models.py
---------
Endpoint d'information sur les modèles disponibles.

GET /api/v1/models → liste les modèles et leurs métriques.

La route POST /models/{name}/select a été supprimée : elle modifiait
l'état serveur, ce qui viole le principe stateless de REST.
Le choix du modèle se fait désormais via le query param de /predict.
"""

from fastapi import APIRouter, Depends

from app.dependencies import get_model_service
from app.schemas.model_info import ModelInfo, ModelListResponse
from app.services.model_service import ModelService

router = APIRouter()


@router.get("/models", response_model=ModelListResponse)
def list_models(
    service: ModelService = Depends(get_model_service),
) -> ModelListResponse:
    """
    Retourne tous les modèles disponibles avec leurs métriques.

    Utilisé par le frontend pour peupler le sélecteur de modèle
    et afficher les scores MAE / RMSE / R².
    """
    return ModelListResponse(
        models=[ModelInfo(**m) for m in service.list_models()],
        active_model=service.get_default_model(),
    )
