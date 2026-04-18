"""
dependencies.py
---------------
Définit les dépendances injectables FastAPI.

Le pattern d'injection de dépendances de FastAPI permet de partager
des ressources (ici le ModelService) entre les routes sans les passer
manuellement à chaque fonction.

Pourquoi un singleton ici et pas dans model_service.py :
  model_service.py définit la CLASSE — la logique.
  dependencies.py crée L'INSTANCE — le singleton partagé.
  Cette séparation permet de remplacer facilement l'instance en tests
  (on peut injecter un faux service sans modifier model_service.py).
"""

from app.services.model_service import ModelService

# Instance unique du service, partagée par toutes les routes.
# Créée au chargement du module — avant même que FastAPI démarre.
# Les modèles ne sont PAS encore chargés ici : c'est fait dans le
# lifespan de main.py, après que l'environnement est prêt.
_model_service = ModelService()


def get_model_service() -> ModelService:
    """
    Dépendance FastAPI : retourne le ModelService singleton.

    Usage dans une route :
        from fastapi import Depends
        from app.dependencies import get_model_service

        @router.post("/predict")
        def predict(service: ModelService = Depends(get_model_service)):
            return service.predict(...)

    FastAPI appelle get_model_service() à chaque requête et injecte
    le résultat dans le paramètre "service". Comme on retourne toujours
    la même instance (_model_service), c'est efficace.
    """
    return _model_service
