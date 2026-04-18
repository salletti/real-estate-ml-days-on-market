"""
model_service.py
----------------
Couche service : fait le lien entre l'API FastAPI et le monde ML.

Architecture stateless :
  Chaque requête apporte avec elle le nom du modèle à utiliser (query param).
  Le service ne maintient aucun "modèle actif" — il reçoit un nom, il prédit.
  C'est conforme au principe REST : une requête doit contenir toutes les
  informations nécessaires à son traitement.

Responsabilités :
  - Charger tous les modèles en mémoire au démarrage (une seule fois)
  - Prédire avec le modèle demandé (ou le meilleur par défaut)
  - Prédire avec tous les modèles en parallèle
  - Exposer les informations sur les modèles disponibles
"""

import logging
from typing import Any

from fastapi import HTTPException

from app.ml import predictor
from app.ml.registry import ModelRegistry

logger = logging.getLogger(__name__)


class ModelService:
    def __init__(self) -> None:
        self._registry: dict[str, dict[str, Any]] = {}
        self._best_model: str | None = None  # calculé une fois au chargement

    def load(self, model_dir: str, default_model: str = "xgboost") -> None:
        """
        Charge tous les modèles depuis le dossier models/.
        Appelé une seule fois au démarrage via le lifespan de FastAPI.
        """
        logger.info(f"Loading models from '{model_dir}'...")
        self._registry = ModelRegistry.load_all(model_dir)

        if not self._registry:
            logger.warning(
                "No models loaded. Run 'python -m scripts.train_models' first."
            )
            return

        # Le "meilleur modèle" est calculé une fois à l'initialisation.
        # Il sert de fallback quand aucun modèle n'est spécifié dans la requête.
        if default_model in self._registry:
            self._best_model = default_model
        else:
            self._best_model = ModelRegistry.get_best_model(self._registry)

        available = list(self._registry.keys())
        logger.info(f"Default model: '{self._best_model}' | Available: {available}")

    # ------------------------------------------------------------------
    # Prédiction stateless
    # ------------------------------------------------------------------

    def predict(
        self, features: dict[str, Any], model_name: str | None = None
    ) -> dict[str, Any]:
        """
        Prédit avec le modèle spécifié, ou le meilleur par défaut.

        Args:
            features   : les 17 features du bien
            model_name : nom du modèle (query param optionnel).
                         Si None → utilise _best_model.

        Raises:
            HTTPException 503 si aucun modèle n'est chargé
            HTTPException 404 si le modèle demandé n'existe pas
        """
        self._assert_models_loaded()

        name = model_name or self._best_model

        if name not in self._registry:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{name}' not found. Available: {list(self._registry.keys())}",  # noqa: E501
            )

        entry = self._registry[name]
        return predictor.predict(
            features=features,
            pipeline=entry["pipeline"],
            metadata=entry["metadata"],
        )

    def predict_all(self, features: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Prédit avec TOUS les modèles et retourne les résultats côte à côte.
        Permet à l'utilisateur de comparer les prédictions des 3 modèles.
        """
        self._assert_models_loaded()

        return [
            predictor.predict(
                features=features,
                pipeline=entry["pipeline"],
                metadata=entry["metadata"],
            )
            for entry in self._registry.values()
        ]

    # ------------------------------------------------------------------
    # Informations sur les modèles
    # ------------------------------------------------------------------

    def list_models(self) -> list[dict[str, Any]]:
        """Retourne les métadonnées de tous les modèles disponibles."""
        return [entry["metadata"] for entry in self._registry.values()]

    def get_default_model(self) -> str | None:
        return self._best_model

    def get_available_models(self) -> list[str]:
        return list(self._registry.keys())

    # ------------------------------------------------------------------
    # Utilitaire interne
    # ------------------------------------------------------------------

    def _assert_models_loaded(self) -> None:
        if not self._registry:
            raise HTTPException(
                status_code=503,
                detail="No ML models loaded. Run 'python -m scripts.train_models' first.",  # noqa: E501
            )
