# =============================================================================
# TESTS FONCTIONNELS — POST /api/v1/predict et /predict/all
#
# On teste les routes HTTP complètes avec des mocks du service ML.
# La logique ML est testée dans test_predictor.py — ici on teste
# uniquement le contrat HTTP : status codes, structure JSON, validation.
# =============================================================================

from fastapi import HTTPException


# =============================================================================
# POST /api/v1/predict
# =============================================================================

def test_predict_returns_200(client, mock_service, sample_features, sample_prediction):
    """Un payload valide doit retourner HTTP 200."""
    mock_service.predict.return_value = sample_prediction

    response = client.post("/api/v1/predict", json=sample_features)

    assert response.status_code == 200


def test_predict_response_structure(client, mock_service, sample_features, sample_prediction):
    """La réponse doit contenir toutes les clés attendues."""
    mock_service.predict.return_value = sample_prediction

    data = client.post("/api/v1/predict", json=sample_features).json()

    assert "predicted_days" in data
    assert "lower_bound" in data
    assert "upper_bound" in data
    assert "model_used" in data
    assert "model_metrics" in data


def test_predict_calls_service_with_correct_model(
    client, mock_service, sample_features, sample_prediction
):
    """
    Le query param ?model= doit être transmis au service.

    PHP équivalent : vérifier qu'un Controller appelle bien
    $service->predict($data, 'random_forest') avec les bons arguments.

    assert_called_once_with() = ->shouldReceive()->once()->with() en Mockery.
    """
    mock_service.predict.return_value = sample_prediction

    client.post("/api/v1/predict?model=random_forest", json=sample_features)

    # On vérifie que predict() a été appelé avec model_name="random_forest"
    mock_service.predict.assert_called_once()
    call_kwargs = mock_service.predict.call_args.kwargs
    assert call_kwargs.get("model_name") == "random_forest"


def test_predict_default_model_when_no_query_param(
    client, mock_service, sample_features, sample_prediction
):
    """Sans query param, model_name doit être None (le service choisit le défaut)."""
    mock_service.predict.return_value = sample_prediction

    client.post("/api/v1/predict", json=sample_features)

    call_kwargs = mock_service.predict.call_args.kwargs
    assert call_kwargs.get("model_name") is None


def test_predict_unknown_model_returns_404(client, mock_service, sample_features):
    """
    Si le modèle demandé n'existe pas, le service lève HTTPException 404.
    FastAPI doit le convertir en réponse HTTP 404.
    """
    # On configure le mock pour simuler une HTTPException 404
    # PHP équivalent : $mock->method('predict')->willThrowException(new NotFoundHttpException())
    mock_service.predict.side_effect = HTTPException(
        status_code=404, detail="Model 'unknown' not found."
    )

    response = client.post("/api/v1/predict?model=unknown", json=sample_features)

    assert response.status_code == 404


def test_predict_invalid_body_returns_422(client, mock_service):
    """
    Un body invalide (surface négative) doit retourner HTTP 422.
    C'est Pydantic qui valide — le service n'est même pas appelé.

    422 Unprocessable Entity = la réponse FastAPI/Pydantic pour les erreurs de validation.
    PHP équivalent : un 400 Bad Request avec les détails de validation.
    """
    invalid_payload = {"surface": -10, "rooms": 3}  # incomplet + surface invalide

    response = client.post("/api/v1/predict", json=invalid_payload)

    assert response.status_code == 422
    # Le service ne doit pas avoir été appelé du tout
    mock_service.predict.assert_not_called()


def test_predict_no_models_loaded_returns_503(client, mock_service, sample_features):
    """Si aucun modèle n'est chargé, le service lève 503 Service Unavailable."""
    mock_service.predict.side_effect = HTTPException(
        status_code=503, detail="No ML models loaded."
    )

    response = client.post("/api/v1/predict", json=sample_features)

    assert response.status_code == 503


# =============================================================================
# POST /api/v1/predict/all
# =============================================================================

def test_predict_all_returns_200(client, mock_service, sample_features, sample_prediction):
    """L'endpoint /predict/all doit retourner HTTP 200."""
    mock_service.predict_all.return_value = [sample_prediction, sample_prediction, sample_prediction]

    response = client.post("/api/v1/predict/all", json=sample_features)

    assert response.status_code == 200


def test_predict_all_returns_three_predictions(
    client, mock_service, sample_features, sample_prediction
):
    """La réponse doit contenir exactement 3 prédictions (une par modèle)."""
    mock_service.predict_all.return_value = [
        {**sample_prediction, "model_used": "xgboost"},
        {**sample_prediction, "model_used": "random_forest"},
        {**sample_prediction, "model_used": "linear_regression"},
    ]

    data = client.post("/api/v1/predict/all", json=sample_features).json()

    assert "predictions" in data
    assert len(data["predictions"]) == 3


def test_predict_all_calls_predict_all_service(
    client, mock_service, sample_features, sample_prediction
):
    """
    /predict/all doit appeler predict_all() sur le service, pas predict().
    Vérifie que le bon endpoint appelle la bonne méthode.
    """
    mock_service.predict_all.return_value = [sample_prediction]

    client.post("/api/v1/predict/all", json=sample_features)

    mock_service.predict_all.assert_called_once()
    mock_service.predict.assert_not_called()
