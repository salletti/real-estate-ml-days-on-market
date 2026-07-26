# Architecture de l'API Backend

Le backend est une application FastAPI chargée de charger les modèles entraînés, valider les requêtes, exécuter les prédictions et retourner les métriques.

## Architecture en Couches

```text
requête HTTP
  -> routes
  -> services
  -> ml
```

Responsabilités :

| Couche | Rôle |
|---|---|
| `routes/` | Transport HTTP, validation, forme des réponses |
| `services/` | Orchestration applicative |
| `ml/` | Génération des données, preprocessing, entraînement, registry, prédiction |
| `schemas/` | Modèles Pydantic de requêtes et réponses |

Les routes ne chargent pas directement les fichiers `.joblib`. La couche ML ne connaît pas HTTP. Chaque couche garde une responsabilité claire.

## Design Stateless

Les requêtes de prédiction sont stateless. Le modèle est choisi avec un query parameter :

```text
POST /api/v1/predict?model=random_forest
```

Si aucun modèle n'est fourni, le modèle par défaut est utilisé.

Cela évite un état serveur partagé. Deux utilisateurs peuvent appeler deux modèles différents au même moment sans interférence.

## Validation Pydantic

FastAPI utilise les schemas Pydantic pour valider automatiquement les entrées.

Une surface négative ou un DPE inconnu déclenche une erreur HTTP de validation avant d'atteindre la logique de prédiction.

## Injection de Dépendances

L'API injecte le service de modèles via les dépendances FastAPI.

```python
@router.post("/predict")
def predict(
    request: PredictionRequest,
    service: ModelService = Depends(get_model_service),
):
    ...
```

Cela garde les routes courtes et rend le service réutilisable.

## Lifespan

Les modèles sont chargés une seule fois au démarrage de l'API.

```text
démarrage -> chargement du registry et des pipelines
requête   -> réutilisation des modèles chargés
arrêt     -> nettoyage si nécessaire
```

Charger les modèles à chaque requête serait trop coûteux.

## Endpoints

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Statut de l'API et nombre de modèles chargés |
| `GET` | `/api/v1/models` | Liste des modèles publics et métriques |
| `POST` | `/api/v1/predict` | Prédiction avec un modèle |
| `POST` | `/api/v1/predict/all` | Prédiction avec tous les modèles publics |

## Exemple de Requête

```json
{
  "surface": 75,
  "rooms": 3,
  "bathrooms": 1,
  "age": 15,
  "listing_price": 320000,
  "market_price_m2": 4200,
  "floor": 2,
  "energy_rating": "C",
  "condition": "good",
  "property_type": "apartment",
  "city": "Paris",
  "neighborhood": "Marais",
  "zipcode": "75003",
  "balcony": true,
  "terrace": false,
  "parking": false,
  "furnished": false
}
```

## Exemple de Réponse

```json
{
  "predicted_days": 47,
  "lower_bound": 28,
  "upper_bound": 66,
  "model_used": "xgboost",
  "model_metrics": {
    "mae": 15.42,
    "rmse": 19.4,
    "r2": 0.746
  }
}
```

La documentation interactive est disponible sur `/docs` quand le backend tourne.
