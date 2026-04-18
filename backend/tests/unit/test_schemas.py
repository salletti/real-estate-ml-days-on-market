# =============================================================================
# TESTS UNITAIRES — Schémas Pydantic
#
# On teste que PredictionRequest valide correctement les données entrantes.
# Pydantic est notre première ligne de défense : il rejette les données
# invalides avant même qu'elles atteignent la logique ML.
#
# Deux types de tests ici :
#   - "happy path"  : des données valides → l'objet est créé sans erreur
#   - "sad path"    : des données invalides → ValidationError levée
# =============================================================================

import pytest
from pydantic import ValidationError

from app.schemas.prediction import PredictionRequest


# -----------------------------------------------------------------------------
# FIXTURE — un dictionnaire de features valides réutilisé dans tous les tests
#
# Une "fixture" en pytest = une valeur ou un objet préparé à l'avance
# qu'on peut injecter dans n'importe quel test en ajoutant son nom
# comme paramètre de la fonction de test.
#
# Ici c'est une simple fonction, décorée avec @pytest.fixture.
# Quand un test déclare `valid_payload` en paramètre, pytest appelle
# automatiquement cette fonction et lui passe le résultat.
# -----------------------------------------------------------------------------
@pytest.fixture
def valid_payload() -> dict:
    """Données minimales valides pour créer un PredictionRequest."""
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


# =============================================================================
# HAPPY PATH — les données valides doivent passer sans erreur
# =============================================================================

def test_valid_request_is_accepted(valid_payload):
    """Un payload complet et valide doit créer l'objet sans erreur."""
    # Si Pydantic lève une exception ici → ce test échoue automatiquement
    request = PredictionRequest(**valid_payload)

    # On vérifie aussi que les valeurs sont bien stockées
    assert request.surface == 65.0
    assert request.city == "Paris"
    assert request.energy_rating == "C"
    assert request.balcony is True


def test_all_energy_ratings_accepted(valid_payload):
    """Chaque valeur de A à G doit être acceptée."""
    for rating in ["A", "B", "C", "D", "E", "F", "G"]:
        payload = {**valid_payload, "energy_rating": rating}
        request = PredictionRequest(**payload)
        assert request.energy_rating == rating


def test_all_conditions_accepted(valid_payload):
    """Chaque état du bien doit être accepté."""
    for condition in ["new", "good", "fair", "poor"]:
        payload = {**valid_payload, "condition": condition}
        request = PredictionRequest(**payload)
        assert request.condition == condition


def test_all_property_types_accepted(valid_payload):
    """Chaque type de bien doit être accepté."""
    for ptype in ["apartment", "house", "studio", "penthouse", "loft"]:
        payload = {**valid_payload, "property_type": ptype}
        request = PredictionRequest(**payload)
        assert request.property_type == ptype


# =============================================================================
# SAD PATH — les données invalides doivent lever une ValidationError
# =============================================================================

def test_negative_surface_rejected(valid_payload):
    """Une surface négative doit être refusée (gt=0 dans le schéma)."""
    with pytest.raises(ValidationError) as exc_info:
        PredictionRequest(**{**valid_payload, "surface": -10.0})

    # On vérifie que l'erreur mentionne bien le champ "surface"
    # exc_info.value est l'exception elle-même
    assert "surface" in str(exc_info.value)


def test_zero_surface_rejected(valid_payload):
    """Surface = 0 doit être refusée (gt=0 signifie strictement supérieur à 0)."""
    with pytest.raises(ValidationError):
        PredictionRequest(**{**valid_payload, "surface": 0})


def test_negative_price_rejected(valid_payload):
    """Un prix négatif doit être refusé."""
    with pytest.raises(ValidationError):
        PredictionRequest(**{**valid_payload, "listing_price": -1000})


def test_invalid_energy_rating_rejected(valid_payload):
    """Un DPE invalide (ex: 'Z') doit être refusé."""
    with pytest.raises(ValidationError):
        PredictionRequest(**{**valid_payload, "energy_rating": "Z"})


def test_invalid_condition_rejected(valid_payload):
    """Un état invalide doit être refusé."""
    with pytest.raises(ValidationError):
        PredictionRequest(**{**valid_payload, "condition": "excellent"})


def test_invalid_property_type_rejected(valid_payload):
    """Un type de bien inconnu doit être refusé."""
    with pytest.raises(ValidationError):
        PredictionRequest(**{**valid_payload, "property_type": "castle"})


def test_too_many_rooms_rejected(valid_payload):
    """Plus de 20 pièces doit être refusé (le=20 dans le schéma)."""
    with pytest.raises(ValidationError):
        PredictionRequest(**{**valid_payload, "rooms": 25})


def test_missing_required_field_rejected():
    """Un payload incomplet (sans surface) doit être refusé."""
    with pytest.raises(ValidationError) as exc_info:
        PredictionRequest(
            # surface manquante intentionnellement
            rooms=3,
            bathrooms=1,
            age=10,
            listing_price=200000,
            market_price_m2=4000,
            floor=1,
            energy_rating="B",
            condition="good",
            property_type="apartment",
            city="Lyon",
            neighborhood="Croix-Rousse",
            zipcode="69001",
            balcony=False,
            terrace=False,
            parking=False,
            furnished=False,
        )
    assert "surface" in str(exc_info.value)
