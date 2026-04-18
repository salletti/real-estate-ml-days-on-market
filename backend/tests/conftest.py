# =============================================================================
# CONFTEST — Fixtures partagées entre tous les tests
#
# PHP équivalent : un trait ou une classe abstraite de test avec setUp().
# Mais ici les fixtures sont injectées automatiquement par nom de paramètre —
# pas besoin d'hériter d'une classe ou d'appeler parent::setUp().
# =============================================================================

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_model_service


# -----------------------------------------------------------------------------
# FIXTURE : mock_service
#
# MagicMock (unittest.mock) ≈ Mockery::mock() en PHP.
# Il crée un objet factice qui accepte n'importe quel appel de méthode
# et retourne un MagicMock par défaut — on configure ensuite ce qu'on veut.
#
# scope="function" (défaut) = recréé à chaque test, comme setUp() en PHPUnit.
# scope="session" = créé une seule fois pour toute la suite (setUpBeforeClass).
# -----------------------------------------------------------------------------
@pytest.fixture
def mock_service():
    return MagicMock()


# -----------------------------------------------------------------------------
# FIXTURE : client
#
# TestClient monte l'application FastAPI en mémoire.
# app.dependency_overrides remplace get_model_service par notre mock —
# toutes les routes qui font Depends(get_model_service) recevront le mock.
#
# C'est l'équivalent de $kernel->getContainer()->set(ModelService::class, $mock)
# en Symfony, ou app()->instance() en Laravel.
# -----------------------------------------------------------------------------
@pytest.fixture
def client(mock_service):
    app.dependency_overrides[get_model_service] = lambda: mock_service
    with TestClient(app) as c:
        yield c
    # Cleanup : on remet les vraies dépendances après le test
    app.dependency_overrides.clear()


# -----------------------------------------------------------------------------
# FIXTURE : sample_features
#
# Payload valide réutilisé dans les tests fonctionnels.
# Défini ici pour ne pas le dupliquer dans chaque fichier de test.
# -----------------------------------------------------------------------------
@pytest.fixture
def sample_features():
    return {
        "surface": 65.0,
        "rooms": 3,
        "bathrooms": 1,
        "age": 15,
        "listing_price": 320000.0,
        "market_price_m2": 4800.0,
        "floor": 2,
        "energy_rating": "C",
        "condition": "good",
        "property_type": "apartment",
        "city": "Paris",
        "neighborhood": "Montmartre",
        "zipcode": "75018",
        "balcony": True,
        "terrace": False,
        "parking": True,
        "furnished": False,
    }


# -----------------------------------------------------------------------------
# FIXTURE : sample_prediction
#
# Réponse factice d'une prédiction — utilisée pour configurer le mock_service.
# -----------------------------------------------------------------------------
@pytest.fixture
def sample_prediction():
    return {
        "predicted_days": 47,
        "lower_bound": 28,
        "upper_bound": 66,
        "model_used": "xgboost",
        "model_metrics": {"mae": 9.97, "rmse": 12.78, "r2": 0.89},
    }
