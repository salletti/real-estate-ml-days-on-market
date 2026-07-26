# Days on Market Backend

Backend FastAPI de l'application Days on Market.

Il charge les pipelines scikit-learn/XGBoost entraînés, expose les endpoints de prédiction, et retourne les métriques des modèles avec une fourchette de confiance.

## Stack

- Python 3.11
- FastAPI
- Pydantic
- scikit-learn
- XGBoost
- joblib
- Ruff
- mypy
- pytest

## Lancer avec Docker

Depuis la racine du projet :

```bash
docker compose up --build -d
docker compose exec backend python -m scripts.train_models
```

L'API est disponible ici :

- Health check : `http://localhost:8000/health`
- Swagger UI : `http://localhost:8000/docs`

## Lancer en Local

```bash
cd backend
pip install -r requirements.txt
python -m scripts.train_models
uvicorn app.main:app --reload
```

## Structure

```text
backend/
├── app/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── config.py            # Configuration
│   ├── dependencies.py      # Dépendances applicatives
│   ├── routes/              # Endpoints HTTP
│   ├── schemas/             # Modèles Pydantic
│   ├── services/            # Services applicatifs
│   └── ml/                  # Données, entraînement, prédiction
├── models/                  # Fichiers .joblib et métadonnées générés
├── scripts/
│   └── train_models.py      # CLI d'entraînement
├── tests/
├── requirements.txt
├── pyproject.toml
└── Dockerfile
```

## Endpoints

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Statut de l'API et nombre de modèles chargés |
| `GET` | `/api/v1/models` | Modèles publics disponibles et métriques |
| `POST` | `/api/v1/predict?model=xgboost` | Prédiction avec un modèle |
| `POST` | `/api/v1/predict/all` | Prédiction avec tous les modèles publics |

## Qualité

```bash
docker compose exec backend ruff check app/
docker compose exec backend ruff format --check app/
docker compose exec backend mypy app/
docker compose exec backend pytest
```

Pour appliquer le formatage :

```bash
docker compose exec backend ruff format app/
```

## Documentation

La documentation pédagogique a été déplacée dans le répertoire `docs/` à la racine :

- [Vue d'ensemble Machine Learning](../docs/machine-learning.md)
- [Dataset et features](../docs/data.md)
- [Pipeline de preprocessing](../docs/preprocessing.md)
- [Comparaison des modèles](../docs/models.md)
- [Architecture de l'API backend](../docs/api-backend.md)
