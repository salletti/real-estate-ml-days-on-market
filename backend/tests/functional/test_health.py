# =============================================================================
# TESTS FONCTIONNELS — GET /health
#
# TestClient envoie de vraies requêtes HTTP à l'app FastAPI montée en mémoire.
# PHP équivalent : KernelBrowser (Symfony) ou TestCase->get() (Laravel).
#
# Les fixtures `client` et `mock_service` viennent de tests/conftest.py —
# pytest les injecte automatiquement par nom de paramètre.
# =============================================================================


def test_health_returns_200(client, mock_service):
    """L'endpoint /health doit retourner HTTP 200."""
    # On configure le mock : list_models() retourne 3 modèles fictifs
    # PHP équivalent : $mock->method('listModels')->willReturn([...])
    mock_service.list_models.return_value = [{}, {}, {}]
    mock_service.get_active_model_name.return_value = "xgboost"

    response = client.get("/health")

    assert response.status_code == 200


def test_health_response_structure(client, mock_service):
    """La réponse doit contenir status, active_model et models_loaded."""
    mock_service.list_models.return_value = [{}, {}, {}]
    mock_service.get_active_model_name.return_value = "xgboost"

    data = client.get("/health").json()

    assert data["status"] == "ok"
    assert data["active_model"] == "xgboost"
    assert data["models_loaded"] == 3


def test_health_with_no_models(client, mock_service):
    """Même sans modèles chargés, /health doit répondre 200 (l'API est vivante)."""
    mock_service.list_models.return_value = []
    mock_service.get_active_model_name.return_value = None

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["models_loaded"] == 0
