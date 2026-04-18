# =============================================================================
# TESTS UNITAIRES — predictor.py
#
# On teste la fonction predict() en isolation complète.
# Le pipeline sklearn est mocké — on ne charge aucun vrai modèle.
#
# PHP équivalent : tester un Service en mockant son Repository.
# unittest.mock.MagicMock = PHPUnit createMock() / Mockery mock()
# =============================================================================

import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from app.ml.predictor import predict, _compute_confidence_interval


# -----------------------------------------------------------------------------
# FIXTURES locales — spécifiques à ce fichier de test
# -----------------------------------------------------------------------------

@pytest.fixture
def features():
    """Features brutes d'entrée — sans price_ratio (calculé dans predict())."""
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


@pytest.fixture
def mock_pipeline():
    """
    Pipeline sklearn mocké.

    named_steps est un dict-like → on utilise __getitem__ pour mocker
    l'accès par clé (pipeline.named_steps["preprocessor"]).

    PHP équivalent : un ArrayAccess mocké, ou $container->get('preprocessor').
    """
    pipeline = MagicMock()

    # pipeline.predict(df) retourne un array numpy d'une valeur
    pipeline.predict.return_value = np.array([47.3])

    # pipeline.named_steps["preprocessor"] et ["model"] pour Random Forest
    preprocessor = MagicMock()
    preprocessor.transform.return_value = np.zeros((1, 10))

    # Simuler 3 arbres de décision avec des prédictions différentes
    tree1, tree2, tree3 = MagicMock(), MagicMock(), MagicMock()
    tree1.predict.return_value = np.array([45.0])
    tree2.predict.return_value = np.array([48.0])
    tree3.predict.return_value = np.array([50.0])

    rf_model = MagicMock()
    rf_model.estimators_ = [tree1, tree2, tree3]

    # named_steps["preprocessor"] et named_steps["model"]
    pipeline.named_steps.__getitem__.side_effect = lambda key: {
        "preprocessor": preprocessor,
        "model": rf_model,
    }[key]

    return pipeline


@pytest.fixture
def xgboost_metadata():
    return {
        "name": "xgboost",
        "algorithm": "xgboost",
        "residual_std": 10.0,
        "mae": 9.97,
        "rmse": 12.78,
        "r2": 0.89,
    }


@pytest.fixture
def rf_metadata():
    return {
        "name": "random_forest",
        "algorithm": "random_forest",
        "residual_std": 12.0,
        "mae": 10.92,
        "rmse": 13.80,
        "r2": 0.87,
    }


# =============================================================================
# TESTS — Structure de la réponse
# =============================================================================

def test_predict_returns_expected_keys(features, mock_pipeline, xgboost_metadata):
    """La réponse doit contenir exactement les clés attendues par le frontend."""
    result = predict(features, mock_pipeline, xgboost_metadata)

    assert "predicted_days" in result
    assert "lower_bound" in result
    assert "upper_bound" in result
    assert "model_used" in result
    assert "model_metrics" in result


def test_predict_model_used_matches_metadata(features, mock_pipeline, xgboost_metadata):
    """model_used doit correspondre au nom dans les métadonnées."""
    result = predict(features, mock_pipeline, xgboost_metadata)
    assert result["model_used"] == "xgboost"


def test_predict_days_is_positive_integer(features, mock_pipeline, xgboost_metadata):
    """predicted_days doit être un entier strictement positif."""
    result = predict(features, mock_pipeline, xgboost_metadata)
    assert isinstance(result["predicted_days"], int)
    assert result["predicted_days"] >= 1


def test_predict_bounds_are_coherent(features, mock_pipeline, xgboost_metadata):
    """lower_bound doit être inférieur ou égal à upper_bound."""
    result = predict(features, mock_pipeline, xgboost_metadata)
    assert result["lower_bound"] <= result["predicted_days"] <= result["upper_bound"]


# =============================================================================
# TESTS — Calcul de price_ratio
#
# price_ratio = listing_price / (surface × market_price_m2)
# C'est une feature dérivée critique — elle est la plus prédictive du modèle.
# =============================================================================

def test_price_ratio_is_calculated(features, mock_pipeline, xgboost_metadata):
    """
    On vérifie que pipeline.predict() est appelé avec un DataFrame
    qui contient la colonne price_ratio (calculée dans predict()).

    PHP équivalent : vérifier qu'un service transforme bien les données
    avant de les passer au repository.
    """
    predict(features, mock_pipeline, xgboost_metadata)

    # On récupère le DataFrame passé à pipeline.predict()
    call_args = mock_pipeline.predict.call_args
    df_passed = call_args[0][0]  # premier argument positionnel

    assert "price_ratio" in df_passed.columns

    # Vérification du calcul : 320000 / (65 × 4800) ≈ 1.026
    expected_ratio = 320000.0 / (65.0 * 4800.0)
    assert abs(df_passed["price_ratio"].iloc[0] - expected_ratio) < 0.001


# =============================================================================
# TESTS — Cas limites
# =============================================================================

def test_very_low_prediction_is_clamped_to_1(features, mock_pipeline, xgboost_metadata):
    """
    Si le modèle prédit une valeur négative ou nulle, on force à 1 jour minimum.
    max(1, ...) dans predictor.py.
    """
    mock_pipeline.predict.return_value = np.array([-5.0])
    result = predict(features, mock_pipeline, xgboost_metadata)
    assert result["predicted_days"] == 1


def test_lower_bound_is_at_least_1(features, mock_pipeline, xgboost_metadata):
    """lower_bound ne peut pas être inférieur à 1 jour."""
    mock_pipeline.predict.return_value = np.array([2.0])  # prédiction très basse
    result = predict(features, mock_pipeline, xgboost_metadata)
    assert result["lower_bound"] >= 1


# =============================================================================
# TESTS — Intervalle de confiance selon le type de modèle
# =============================================================================

def test_rf_uses_tree_variance_for_confidence(features, mock_pipeline, rf_metadata):
    """
    Pour Random Forest, l'intervalle est basé sur la variance inter-arbres.
    Avec 3 arbres prédisant [45, 48, 50], l'écart-type est ~2.16 → marge ~4 jours.
    """
    result = predict(features, mock_pipeline, rf_metadata)
    # L'intervalle doit être non nul
    assert result["upper_bound"] > result["lower_bound"]


def test_xgboost_uses_residual_std(features, mock_pipeline, xgboost_metadata):
    """
    Pour XGBoost, l'intervalle est basé sur residual_std=10.0.
    Marge = round(1.96 × 10) = 20 jours.
    """
    result = predict(features, mock_pipeline, xgboost_metadata)
    predicted = result["predicted_days"]
    # La marge théorique est 20 jours
    assert result["upper_bound"] == predicted + 20
