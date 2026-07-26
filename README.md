![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-ML-orange)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

# Days on Market

Days on Market est une application full-stack de Machine Learning qui estime le temps de vente d'un bien immobilier.

L'utilisateur saisit les caractéristiques d'un bien, l'API FastAPI calcule une prédiction, et l'interface React compare les résultats de plusieurs modèles.

## Fonctionnalités

- Formulaire immobilier avec 17 features : surface, prix, ville, DPE, état, équipements, etc.
- Prédictions en parallèle avec XGBoost, Random Forest et Linear Regression
- Fourchette de confiance pour chaque prédiction
- Comparaison des modèles avec MAE, RMSE et R2
- Environnement local avec Docker Compose
- Documentation pédagogique dédiée au pipeline Machine Learning

## Stack Technique

| Couche | Technologie |
|---|---|
| Backend | FastAPI, Python 3.11 |
| Machine Learning | scikit-learn, XGBoost |
| Frontend | React 18, TypeScript, Vite |
| Formulaires | react-hook-form |
| Client HTTP | Axios |
| Infrastructure | Docker, Docker Compose |
| Qualité | Ruff, mypy, ESLint, Prettier, Vitest, pytest |

## Démarrage Rapide

### Prérequis

- Docker
- Docker Compose

### Lancer l'application

```bash
docker compose up --build -d
docker compose exec backend python -m scripts.train_models
```

Puis ouvrir :

- Frontend : `http://localhost:3000`
- Documentation API : `http://localhost:8000/docs`

### Arrêter l'application

```bash
docker compose down
```

## API

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Statut de l'API et des modèles chargés |
| `GET` | `/api/v1/models` | Modèles disponibles et métriques |
| `POST` | `/api/v1/predict?model=xgboost` | Prédiction avec un modèle |
| `POST` | `/api/v1/predict/all` | Comparaison des prédictions des modèles publics |

La documentation interactive est disponible sur `http://localhost:8000/docs`.

## Machine Learning

Les modèles sont entraînés sur un dataset synthétique de 5 000 biens immobiliers. La target est `days_on_market`.

La feature dérivée la plus importante est :

```text
price_ratio = listing_price / (surface * market_price_m2)
```

Elle indique si un bien est sous-évalué, correctement positionné ou surévalué par rapport au marché local.

| Modèle | Rôle |
|---|---|
| Linear Regression | Baseline simple |
| Random Forest | Ensemble d'arbres robuste |
| XGBoost | Modèle principal de gradient boosting |

Le projet est volontairement pédagogique : il montre comment assembler preprocessing, feature engineering, comparaison de modèles et intervalles de confiance dans une API utilisable.

## Structure

```text
days-on-market/
├── backend/              # API FastAPI et pipeline ML
├── frontend/             # Application React
├── docs/                 # Documentation pédagogique
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

## Développement

Checks backend :

```bash
docker compose exec backend ruff check app/
docker compose exec backend ruff format --check app/
docker compose exec backend mypy app/
docker compose exec backend pytest
```

Checks frontend :

```bash
docker compose --profile lint run --rm frontend-lint npm run lint
docker compose --profile lint run --rm frontend-lint npm run format:check
docker compose --profile lint run --rm frontend-lint npm run test:run
```

## Documentation

- [Sommaire de la documentation](docs/README.md)
- [Vue d'ensemble Machine Learning](docs/machine-learning.md)
- [Dataset et features](docs/data.md)
- [Pipeline de preprocessing](docs/preprocessing.md)
- [Comparaison des modèles](docs/models.md)
- [Architecture de l'API backend](docs/api-backend.md)

## Limites

Ce projet utilise des données synthétiques. Il sert de démonstration technique et pédagogique, pas de système de prédiction immobilier exploitable tel quel en production.

Pour un usage réel, les modèles devraient être entraînés et validés sur des données de marché réelles : transactions, historique d'annonces, signaux géographiques et tendances temporelles.

## Roadmap

- Remplacer ou compléter les données synthétiques par des données réelles
- Ajouter du tuning d'hyperparamètres et de la validation croisée
- Ajouter une validation temporelle pour mesurer le drift marché
- Ajouter des checks CI sur les pull requests
- Documenter le déploiement

## Licence

Ce projet est distribué sous licence [MIT](LICENSE).
