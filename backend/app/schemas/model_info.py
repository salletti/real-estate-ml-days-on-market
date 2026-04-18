"""
model_info.py (schemas)
-----------------------
Schémas pour l'endpoint GET /api/v1/models.
"""

from pydantic import BaseModel


class ModelInfo(BaseModel):
    name: str
    algorithm: str
    mae: float
    rmse: float
    r2: float
    trained_at: str


class ModelListResponse(BaseModel):
    models: list[ModelInfo]
    active_model: str | None  # modèle par défaut (meilleur MAE)
