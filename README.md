# Days on Market

Prédiction du temps de vente d'un bien immobilier — application full-stack avec Machine Learning.

Un agent immobilier saisit les caractéristiques d'un bien et obtient une estimation en jours accompagnée d'une fourchette de confiance, calculée par trois modèles ML comparés en temps réel.

---

## Stack technique

| Couche | Technologie |
|---|---|
| **Backend** | FastAPI + Python 3.11 |
| **Machine Learning** | scikit-learn, XGBoost |
| **Frontend** | React 19, TypeScript, Vite |
| **Formulaires** | react-hook-form |
| **HTTP client** | Axios |
| **Infrastructure** | Docker, Docker Compose |
| **Qualité backend** | Ruff, mypy |

---

## Fonctionnalités

- Formulaire avec 17 features immobilières (surface, prix, ville, DPE, état...)
- Prédiction avec **XGBoost**, **Random Forest** et **Régression Linéaire** en parallèle
- Intervalle de confiance à 95% pour chaque prédiction
- Comparaison des trois modèles avec leurs métriques (MAE, RMSE, R²)
- Explications pédagogiques intégrées sur le fonctionnement du ML

---

## Architecture

```
days-on-market/
├── backend/            # API FastAPI + pipeline ML
│   ├── app/
│   │   ├── routes/     # Endpoints HTTP
│   │   ├── services/   # Logique applicative
│   │   ├── ml/         # Preprocessing, entraînement, prédiction
│   │   └── schemas/    # Modèles Pydantic
│   ├── models/         # Fichiers .joblib générés à l'entraînement
│   └── scripts/        # CLI d'entraînement
├── frontend/           # Application React
│   └── src/
│       ├── components/ # Form, PredictionResult, ModelComparison
│       └── pages/      # HomePage
└── docker-compose.yml
```

---

## Démarrage rapide

### Prérequis

- Docker et Docker Compose

### Lancer l'application

```bash
# Construire et démarrer les services
docker compose up --build -d

# Entraîner les modèles (requis au premier lancement)
docker compose exec backend python -m scripts.train_models

# Frontend : http://localhost:3000
# Backend (Swagger) : http://localhost:8000/docs
```

### Arrêter

```bash
docker compose down
```

---

## API — Endpoints principaux

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Statut de l'API et modèles chargés |
| `GET` | `/api/v1/models` | Liste des modèles et leurs métriques |
| `POST` | `/api/v1/predict?model=xgboost` | Prédiction avec un modèle |
| `POST` | `/api/v1/predict/all` | Prédictions des 3 modèles en parallèle |

Exemple de réponse :

```json
{
  "predicted_days": 47,
  "lower_bound": 28,
  "upper_bound": 66,
  "model_used": "xgboost",
  "model_metrics": { "mae": 15.42, "rmse": 19.40, "r2": 0.89 }
}
```

Documentation interactive : **`http://localhost:8000/docs`**

---

## Modèles ML — Performances

Les modèles sont entraînés sur un dataset synthétique de 5 000 biens immobiliers avec une feature dérivée clé (`price_ratio = listing_price / (surface × market_price_m2)`).

```
Modèle                  MAE      RMSE      R²
────────────────────────────────────────────────
xgboost                ~8 jours  ~11 j    0.89
random_forest          ~8 jours  ~11 j    0.87
linear_regression      ~8 jours  ~11 j    0.89
```

Les trois modèles atteignent R²~0.89 grâce au feature engineering (`price_ratio`). La régression linéaire, normalement limitée, atteint la même précision que XGBoost une fois cette feature ajoutée — illustration concrète de l'importance du feature engineering vs choix du modèle.

---

## Qualité de code

```bash
# Lint
docker compose exec backend ruff check app/

# Format
docker compose exec backend ruff format app/

# Type checking
docker compose exec backend mypy app/

# Tests
docker compose exec backend pytest
```

Un hook `pre-commit` exécute automatiquement Ruff et mypy avant chaque commit.

---

## Documentation détaillée

Le README du backend contient une documentation pédagogique complète sur :
- Le pipeline ML étape par étape (preprocessing, entraînement, évaluation)
- Les trois modèles comparés (Linear Regression, Random Forest, XGBoost)
- L'architecture FastAPI (couches, injection de dépendances, lifespan)
- Les pistes d'amélioration (hyperparameter tuning, données réelles DVF...)

→ [`backend/README.md`](backend/README.md)
