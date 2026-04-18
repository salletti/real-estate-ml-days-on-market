"""
health.py
---------
Endpoint de santé : vérifie que l'API est opérationnelle.

Utilisé par :
  - Render.com pour vérifier que le service est vivant (health check)
  - Le frontend pour afficher un indicateur de statut
  - Les outils de monitoring (UptimeRobot, etc.)
"""

from typing import Any

from fastapi import APIRouter, Depends

from app.dependencies import get_model_service
from app.services.model_service import ModelService

router = APIRouter()


@router.get("/health")
def health(service: ModelService = Depends(get_model_service)) -> dict[str, Any]:
    """
    Retourne le statut de l'API et le modèle actif.

    Exemple de réponse :
        {"status": "ok", "active_model": "xgboost", "models_loaded": 3}
    """
    return {
        "status": "ok",
        "active_model": service.get_default_model(),
        "models_loaded": len(service.list_models()),
    }
