# Days on Market — Backend

API de prédiction du temps de vente d'un bien immobilier.  
Construite avec **FastAPI** + **scikit-learn** + **XGBoost**.

---

## Table des matières

1. [C'est quoi ce projet ?](#cest-quoi-ce-projet-)
2. [Comment fonctionne le Machine Learning ici ?](#comment-fonctionne-le-machine-learning-ici-)
3. [Les données](#les-données)
4. [Le pipeline ML étape par étape](#le-pipeline-ml-étape-par-étape)
5. [X_train, X_test, y_train, y_test — la convention fondamentale](#x_train-x_test-y_train-y_test--la-convention-fondamentale)
6. [Les trois modèles comparés](#les-trois-modèles-comparés)
7. [L'API FastAPI](#lapi-fastapi)
8. [Structure du projet](#structure-du-projet)
9. [Lancer le projet](#lancer-le-projet)
10. [Qualité de code](#qualité-de-code)
11. [Les endpoints](#les-endpoints)

---

## C'est quoi ce projet ?

Un agent immobilier veut savoir : **"Si je mets ce bien en vente aujourd'hui, dans combien de jours aurai-je un acheteur ?"**

Ce backend répond à cette question. On lui donne les caractéristiques d'un bien (surface, prix, ville, état, etc.) et il retourne une estimation en jours, accompagnée d'une fourchette de confiance.

Exemple de réponse :
```json
{
  "predicted_days": 47,
  "lower_bound": 28,
  "upper_bound": 66,
  "model_used": "xgboost"
}
```

Traduction : *"Ce bien devrait se vendre en 47 jours, mais compte entre 28 et 66 jours."*

---

## Comment fonctionne le Machine Learning ici ?

### Le principe fondamental

Un modèle ML est une **fonction mathématique** qui apprend des patterns dans des données historiques, puis les applique à de nouveaux cas.

Dans notre cas :
```
entrée  : surface=75m², prix=320 000€, ville=Paris, état=good...
           ↓
        modèle ML (fonction apprise)
           ↓
sortie  : 47 jours
```

Le modèle ne "comprend" pas l'immobilier. Il a simplement observé des milliers de biens avec leurs caractéristiques et leur temps de vente réel, et a détecté des patterns : *"les biens surévalués restent plus longtemps sur le marché"*, *"les maisons se vendent plus vite que les studios"*, etc.

### Pourquoi les modèles ne comprennent pas les mots

Les modèles ML sont des fonctions mathématiques — ils ne comprennent que des nombres. `"Paris"` ou `"good"` sont du texte, impossible à multiplier ou additionner.

Il faut donc **transformer toutes les données en nombres** avant de les donner au modèle. C'est le rôle du preprocessing.

### X et y — la convention universelle

En ML, on sépare toujours les données en deux parties :

- **X** = les features (les entrées) — tout ce qu'on donne au modèle
- **y** = la target (la sortie) — ce qu'on veut prédire

```
X → surface, rooms, city, energy_rating, parking...  (17 colonnes)
y → days_on_market                                    (1 colonne)
```

La notation vient des maths : `y = f(X)`. Le modèle apprend la fonction `f`.

---

## Les données

Le projet utilise un **dataset synthétique** de 5 000 biens immobiliers générés avec des relations réalistes.

### Pourquoi synthétique ?

Un vrai dataset immobilier propre est difficile à obtenir légalement et gratuitement. Les données synthétiques permettent de contrôler exactement les relations entre features et target — ce qui rend le projet plus pédagogique et reproductible.

### Les 17 features

| Feature | Type | Description |
|---|---|---|
| `surface` | numérique | Superficie en m² |
| `rooms` | numérique | Nombre de pièces |
| `bathrooms` | numérique | Nombre de salles de bain |
| `age` | numérique | Ancienneté du bien en années |
| `listing_price` | numérique | Prix demandé par le vendeur en € |
| `market_price_m2` | numérique | Prix moyen du m² dans la zone |
| `floor` | numérique | Étage (0 = rez-de-chaussée) |
| `energy_rating` | ordinal | DPE de A (meilleur) à G (pire) |
| `condition` | ordinal | État : new, good, fair, poor |
| `property_type` | catégoriel | apartment, house, studio, penthouse, loft |
| `city` | catégoriel | Paris, Lyon, Marseille... |
| `neighborhood` | catégoriel | Marais, Croix-Rousse... |
| `zipcode` | catégoriel | Code postal |
| `balcony` | binaire | 0 ou 1 |
| `terrace` | binaire | 0 ou 1 |
| `parking` | binaire | 0 ou 1 |
| `furnished` | binaire | 0 ou 1 |

### Comment la target est construite

`days_on_market` est calculé avec des règles qui reflètent la réalité :

```
days = 30 (base)
     + price_premium × 200    ← surévaluation = facteur principal
     + condition_penalty       ← poor = +35 jours, new = +0 jour
     + energy_penalty          ← DPE G = +30 jours, DPE A = -5 jours
     + type_effect             ← penthouse = -10 jours, studio = +10 jours
     − parking × 5            ← les équipements réduisent le délai
     + bruit gaussien          ← la réalité n'est jamais déterministe
```

Le bruit gaussien est intentionnel : deux biens identiques ne se vendront jamais exactement au même nombre de jours. Le bruit simule les facteurs non mesurés (vendeur pressé, coup de cœur acheteur, conjoncture locale).

---

## Le pipeline ML étape par étape

### 1. Le preprocessing — transformer le texte en nombres

Avant d'entraîner un modèle, toutes les features doivent devenir numériques. On utilise trois transformations différentes selon le type de feature.

#### StandardScaler (features numériques)

**Problème :** `surface` varie entre 20 et 300, `listing_price` entre 50 000 et 2 000 000. Sans normalisation, le modèle croirait que `listing_price` est 10 000x plus important que `surface` — juste à cause de l'unité.

**Solution :** pour chaque colonne, soustraire la moyenne et diviser par l'écart-type :
```
valeur_transformée = (valeur - moyenne) / écart_type
```

Résultat : toutes les features numériques ont une moyenne de 0 et un écart-type de 1. Elles sont comparables.

```
surface 80m²  →  0.3   (légèrement au-dessus de la moyenne)
surface 300m² →  2.8   (bien au-dessus)
surface 20m²  → -1.4   (en dessous)
```

#### OrdinalEncoder (features avec un ordre logique)

**Problème :** `energy_rating` vaut A, B, C... G. Il y a un ordre réel : A est meilleur que G.

**Solution :** encoder en respectant l'ordre :
```
A → 0,  B → 1,  C → 2,  D → 3,  E → 4,  F → 5,  G → 6
```

Le modèle apprend alors que 6 (G) est associé à plus de jours sur le marché que 0 (A).

**Pourquoi pas OneHotEncoder ici ?**  
OneHotEncoder créerait 7 colonnes séparées (is_A, is_B...) et perdrait l'information d'ordre — le modèle ne saurait plus que B est "entre" A et C.

#### OneHotEncoder (features catégorielles sans ordre)

**Problème :** `property_type` vaut "apartment", "house", "studio"... Il n'y a pas d'ordre. Si on faisait `apartment=1, house=2, studio=3`, le modèle croirait que "house" est deux fois "apartment" — absurde.

**Solution :** créer une colonne binaire par catégorie :
```
property_type="house"   →  [0, 1, 0, 0]   (apartment, house, studio, loft)
property_type="studio"  →  [0, 0, 1, 0]
```

L'option `drop="first"` supprime la première catégorie (redondante). L'option `handle_unknown="ignore"` évite un crash si une ville inconnue arrive à l'inférence : ses colonnes sont mises à 0.

#### Passthrough (features binaires)

`balcony`, `terrace`, `parking`, `furnished` sont déjà 0 ou 1 — aucune transformation nécessaire.

#### ColumnTransformer — l'assemblage final

`ColumnTransformer` est l'objet sklearn qui applique **en parallèle** chaque transformation sur son groupe de colonnes, puis **concatène** les résultats en une seule matrice numérique :

```
surface=80, rooms=3     →  StandardScaler  →  [0.3, -0.2, ...]
energy_rating="C"       →  OrdinalEncoder  →  [2]
property_type="house"   →  OneHotEncoder   →  [0, 1, 0, 0]
balcony=1               →  passthrough     →  [1]
                                                ↓
                        concat  →  [0.3, -0.2, ..., 2, 0, 1, 0, 0, ..., 1]
```

### 2. Le Pipeline sklearn — preprocessor + modèle dans un seul objet

On enchaîne le `ColumnTransformer` et le modèle dans un `Pipeline` sklearn :

```python
Pipeline([
    ("preprocessor", ColumnTransformer(...)),
    ("model",        XGBRegressor(...)),
])
```

**Avantage majeur :** l'objet Pipeline entier est sauvegardé dans un seul fichier `.joblib`. À l'inférence, on donne des données brutes directement — le pipeline gère tout. Pas d'étapes séparées à gérer manuellement.

```python
# Entraînement
pipeline.fit(X_train, y_train)   # apprend preprocessing + modèle en une ligne

# Inférence
pipeline.predict(X_new)          # transforme + prédit en une ligne
```

### 3. La séparation train / test — règle absolue

Avant d'entraîner, on découpe le dataset en deux parties :

```
Dataset (5000 biens)
        ↓  train_test_split(test_size=0.2)
  ┌─────┴─────┐
Train (4000)  Test (1000)
```

- **Train set** : le modèle voit les features ET les vraies réponses → il apprend
- **Test set** : le modèle prédit sans voir les vraies réponses → on évalue l'honnêteté

Si on évaluait sur le train set, le modèle aurait "mémorisé" les réponses. Les métriques seraient excellentes mais sans valeur — comme réviser avec les réponses du contrôle.

### 4. L'évaluation — trois métriques

**MAE (Mean Absolute Error)** — erreur moyenne en jours  
*"Le modèle se trompe en moyenne de X jours."*  
Facile à interpréter, directement en jours.

**RMSE (Root Mean Squared Error)** — similaire à la MAE mais pénalise les grosses erreurs  
*"Si le modèle se trompe de 5 jours sur 9 biens et de 100 jours sur 1 bien, le RMSE sera beaucoup plus élevé que la MAE."*  
Utile pour détecter les outliers.

**R² (coefficient de détermination)** — proportion de variance expliquée  
```
R² = 1.0  → modèle parfait (impossible en pratique)
R² = 0.75 → le modèle explique 75% de la variabilité des données
R² = 0.0  → le modèle ne fait pas mieux que prédire la moyenne tout le temps
R² < 0    → le modèle est pire que prédire la moyenne → quelque chose ne va pas
```

---

## X_train, X_test, y_train, y_test — la convention fondamentale

### La convention X et y

En ML, on sépare toujours les données en deux parties :

- **X** = les features (les entrées) — ce qu'on donne au modèle
- **y** = la target (la sortie) — ce qu'on veut prédire

Dans notre projet :
```
X  →  surface, rooms, city, energy_rating, parking...  (17 colonnes)
y  →  days_on_market                                    (1 colonne)
```

Pourquoi cette notation ? Convention mathématique : `y = f(X)`. Le modèle apprend la fonction `f` qui transforme X en y.

### Le découpage train / test

Une fois qu'on a X et y, on les découpe tous les deux en deux parties :

```
X (5000 lignes × 17 colonnes)  →  X_train (4000 lignes) + X_test (1000 lignes)
y (5000 lignes × 1 colonne)    →  y_train (4000 lignes) + y_test (1000 lignes)
```

La coupure est **verticale** — on garde les mêmes lignes ensemble dans X et y. Le bien numéro 42 reste lié à son `days_on_market`.

```
         X_train              y_train
┌────────────────────┐    ┌──────────┐
│ surface=80, ...    │    │    45    │  ← bien 1
│ surface=55, ...    │    │    12    │  ← bien 2
│ ...                │    │   ...    │
└────────────────────┘    └──────────┘
         X_test               y_test
┌────────────────────┐    ┌──────────┐
│ surface=120, ...   │    │    67    │  ← bien 4001
│ ...                │    │   ...    │
└────────────────────┘    └──────────┘
```

### À quoi sert chaque variable

**`X_train` + `y_train`** → donnés au modèle pendant l'entraînement.  
Le modèle voit les features ET les vraies réponses. Il apprend les patterns.

```python
pipeline.fit(X_train, y_train)
# "Voilà 4000 biens avec leurs caractéristiques ET leur nombre de jours réels.
#  Apprends la relation."
```

**`X_test`** → donné au modèle pour prédire, **sans lui montrer `y_test`**.  
Le modèle prédit comme s'il voyait de nouveaux biens pour la première fois.

```python
y_pred = pipeline.predict(X_test)
# "Voilà 1000 biens que tu n'as jamais vus. Combien de jours vont-ils rester ?"
```

**`y_test`** → gardé de côté pour comparer avec `y_pred`.  
C'est la vérité terrain. On compare `y_pred` vs `y_test` pour calculer les métriques.

```python
mae = mean_absolute_error(y_test, y_pred)
# "En moyenne, de combien de jours le modèle s'est-il trompé ?"
```

### Résumé visuel

```
Entraînement                    Évaluation
─────────────────               ──────────────────────────────────
X_train  ──┐                    X_test  ──→  pipeline.predict()  ──→  y_pred
           ├──→  pipeline.fit()                                          │
y_train  ──┘                    y_test  ─────────────────────────────→  compare
                                                                          │
                                                                     MAE, RMSE, R²
```

Le modèle ne touche **jamais** `y_test` avant l'évaluation. C'est cette séparation qui rend les métriques fiables et honnêtes.

---

## Les trois modèles comparés

### Linear Regression

Le modèle le plus simple : il cherche une **relation linéaire directe** entre les features et la target.

```
days = a×surface + b×price + c×age + ... + constante
```

**Force :** rapide, interprétable, bon comme baseline de référence.  
**Faiblesse :** ne capture pas les relations non-linéaires. Si l'effet du prix dépend de l'état du bien (interaction), la régression linéaire rate ça.

### Random Forest

Un ensemble de **200 arbres de décision** entraînés en parallèle sur des sous-ensembles aléatoires des données (technique du **bagging**).

Chaque arbre apprend indépendamment, la prédiction finale est la **moyenne** des 200 arbres.  
Cette diversité réduit la variance : un seul arbre peut se tromper lourdement, 200 arbres en moyenne se compensent.

**Force :** robuste au bruit, peu sensible au surapprentissage, pas besoin de normalisation des features.  
**Faiblesse :** modèle lourd (200 arbres), moins précis que XGBoost sur données tabulaires.

**Bonus — intervalle de confiance natif :** la dispersion des 200 prédictions individuelles est une mesure naturelle de l'incertitude. Si les arbres sont très en désaccord sur un bien → intervalle large. S'ils convergent → intervalle étroit.

### XGBoost

Gradient Boosting : les arbres sont construits **séquentiellement**. Chaque nouvel arbre corrige les erreurs résiduelles du précédent.

```
Arbre 1  →  prédit 60 jours  (erreur : -7 jours)
Arbre 2  →  corrige l'erreur de l'arbre 1
Arbre 3  →  corrige l'erreur de l'arbre 2
...
Arbre 300 → prédiction finale très affinée
```

**Force :** très précis sur les données tabulaires, gagne régulièrement des compétitions Kaggle.  
**Faiblesse :** plus sensible au surapprentissage, nécessite un tuning des hyperparamètres.

**Différence clé avec Random Forest :**

| | Random Forest | XGBoost |
|---|---|---|
| Construction | Parallèle (bagging) | Séquentielle (boosting) |
| Chaque arbre | Indépendant | Corrige le précédent |
| Résultat final | Moyenne | Somme pondérée |
| Sensibilité | Robuste | Nécessite du tuning |

### Résultats obtenus

```
═══════════════════════════════════════════════════════
  Modèle                  MAE     RMSE       R²
═══════════════════════════════════════════════════════
  linear_regression      24.94   30.59    0.3681
  random_forest          23.36   28.39    0.4560
  xgboost                15.42   19.40    0.7460
═══════════════════════════════════════════════════════
```

XGBoost est clairement le meilleur : MAE de ~15 jours et R² de 0.75 (explique 75% de la variabilité). Ces scores sont réalistes pour un problème immobilier — la target est intrinsèquement bruyante.

---

## L'API FastAPI

### Architecture en couches

```
HTTP Request
    │
    ▼
routes/          ← Transport : reçoit, valide, répond (HTTP)
    │
    ▼
services/        ← Logique applicative : orchestre les appels ML
    │
    ▼
ml/              ← Logique ML : preprocessing, prédiction, registry
```

Chaque couche a une responsabilité unique. Les routes ne savent pas ce qu'est un `.joblib`. Le predictor ne sait pas ce qu'est une requête HTTP.

### Design stateless

L'API est **stateless** : chaque requête contient toutes les informations nécessaires à son traitement. Il n'y a pas d'"état" côté serveur.

Le modèle à utiliser est passé en **query parameter** :
```
POST /api/v1/predict?model=random_forest
```

Sans ce paramètre, le meilleur modèle est utilisé par défaut.

**Pourquoi stateless ?**  
Avec un état côté serveur (ex: "modèle actif"), deux utilisateurs simultanés pourraient interférer : l'un change le modèle actif juste avant que l'autre fasse une prédiction. Avec un query param, chaque requête est totalement indépendante.

### Validation automatique avec Pydantic

FastAPI utilise Pydantic pour valider automatiquement les données entrantes. Si le frontend envoie `surface: -5` ou `energy_rating: "Z"`, FastAPI retourne HTTP 422 avec un message d'erreur clair — sans qu'on écrive une seule ligne de validation.

### L'injection de dépendances

```python
@router.post("/predict")
def predict(
    request: PredictionRequest,
    service: ModelService = Depends(get_model_service),  # ← injection
):
```

`Depends(get_model_service)` demande à FastAPI d'appeler `get_model_service()` et d'injecter le résultat dans le paramètre `service`. Le `ModelService` singleton est ainsi partagé par toutes les routes sans variable globale.

### Le lifespan — chargement des modèles au démarrage

```python
@asynccontextmanager
async def lifespan(app):
    service.load(model_dir=settings.model_dir)  # exécuté une fois au démarrage
    yield
    # arrêt (optionnel)
```

Les modèles sont chargés **une seule fois** au démarrage du serveur, pas à chaque requête. Charger un `.joblib` de 50Mo à chaque appel rendrait l'API inutilisable.

### L'intervalle de confiance

Retourner `47 jours` seul est trompeur. L'API retourne toujours une fourchette :

```
lower_bound = predicted_days - 1.96 × residual_std
upper_bound = predicted_days + 1.96 × residual_std
```

`residual_std` est l'écart-type des erreurs calculé sur le test set pendant l'entraînement. `1.96` est le z-score correspondant à 95% sous distribution normale.

Pour Random Forest, on utilise la variance inter-arbres plutôt que le `residual_std` global — c'est une mesure d'incertitude propre à chaque bien.

---

## Structure du projet

```
backend/
├── app/
│   ├── main.py              # Point d'entrée FastAPI (lifespan, CORS, routers)
│   ├── config.py            # Variables d'environnement (pydantic-settings)
│   ├── dependencies.py      # Singleton ModelService injectable
│   │
│   ├── routes/
│   │   ├── health.py        # GET /health
│   │   ├── predict.py       # POST /api/v1/predict et /predict/all
│   │   └── models.py        # GET /api/v1/models
│   │
│   ├── schemas/
│   │   ├── prediction.py    # PredictionRequest, PredictionResponse
│   │   └── model_info.py    # ModelInfo, ModelListResponse
│   │
│   ├── services/
│   │   └── model_service.py # Orchestre ML : charge, prédit, liste
│   │
│   └── ml/
│       ├── constants.py     # Source de vérité : listes de features, ordres
│       ├── data_generator.py# Génère le dataset synthétique (5000 biens)
│       ├── preprocessor.py  # ColumnTransformer (scaler + encoders)
│       ├── trainer.py       # Entraîne les 3 modèles, évalue, sauvegarde
│       ├── registry.py      # Sauvegarde/chargement des .joblib et .json
│       └── predictor.py     # Inférence + calcul intervalle de confiance
│
├── models/                  # Fichiers .joblib et .json générés à l'entraînement
│   ├── xgboost.joblib
│   ├── xgboost.json
│   └── ...
│
├── scripts/
│   └── train_models.py      # CLI : entraîne et affiche le tableau de métriques
│
├── requirements.txt
└── Dockerfile
```

---

## Lancer le projet

### Avec Docker (recommandé)

```bash
# Depuis la racine du projet
docker compose up --build -d

# Entraîner les modèles (une seule fois, ou après modification du code ML)
docker compose exec backend python -m scripts.train_models

# Logs en temps réel
docker compose logs -f backend
```

### En local (sans Docker)

```bash
cd backend
pip install -r requirements.txt

# Entraîner les modèles
python -m scripts.train_models

# Lancer l'API
uvicorn app.main:app --reload
```

---

## Qualité de code

### Outils

| Outil | Rôle | Config |
|---|---|---|
| **Ruff** | Linter + formatter (remplace flake8, black, isort en un seul outil) | `pyproject.toml` |
| **mypy** | Vérification statique des types Python | `pyproject.toml` |

### Lancer les checks (via Docker)

```bash
# Lint — détecte les erreurs de style, imports mal triés, bugs potentiels
docker compose exec backend ruff check app/

# Vérifier le formatage sans modifier les fichiers
docker compose exec backend ruff format --check app/

# Appliquer le formatage automatiquement
docker compose exec backend ruff format app/

# Corriger les erreurs auto-fixables (imports, annotations dépréciées...)
docker compose exec backend ruff check app/ --fix

# Type checking statique
docker compose exec backend mypy app/
```

### Règles actives (Ruff)

Configurées dans `pyproject.toml` via `select` :

| Code | Catégorie | Exemple détecté |
|---|---|---|
| `E` / `F` | Erreurs pycodestyle / pyflakes | variable inutilisée, import manquant |
| `I` | isort | imports mal triés ou mal groupés |
| `UP` | pyupgrade | `Optional[str]` → `str \| None` |
| `B` | flake8-bugbear | patterns potentiellement dangereux |

### Git hook automatique

Un hook `pre-commit` est installé dans `.git/hooks/pre-commit`. Il exécute automatiquement Ruff (lint + format) et mypy avant chaque `git commit`. Si un check échoue, le commit est bloqué jusqu'à correction.

---

## Les endpoints

### `GET /health`
Vérifie que l'API est opérationnelle.

```json
{"status": "ok", "active_model": "xgboost", "models_loaded": 3}
```

### `GET /api/v1/models`
Liste tous les modèles disponibles avec leurs métriques.

```json
{
  "models": [
    {"name": "xgboost", "mae": 15.42, "rmse": 19.40, "r2": 0.746, "trained_at": "..."},
    {"name": "random_forest", "mae": 23.36, "rmse": 28.39, "r2": 0.456, "trained_at": "..."},
    {"name": "linear_regression", "mae": 24.94, "rmse": 30.59, "r2": 0.368, "trained_at": "..."}
  ],
  "active_model": "xgboost"
}
```

### `POST /api/v1/predict?model=xgboost`
Prédit avec un modèle spécifique (optionnel, défaut = xgboost).

```json
// Body
{
  "surface": 75, "rooms": 3, "bathrooms": 1, "age": 15,
  "listing_price": 320000, "market_price_m2": 4200, "floor": 2,
  "energy_rating": "C", "condition": "good",
  "property_type": "apartment", "city": "Paris",
  "neighborhood": "Marais", "zipcode": "75003",
  "balcony": true, "terrace": false, "parking": false, "furnished": false
}

// Réponse
{
  "predicted_days": 47,
  "lower_bound": 28,
  "upper_bound": 66,
  "model_used": "xgboost",
  "model_metrics": {"mae": 15.42, "rmse": 19.40, "r2": 0.746}
}
```

### `POST /api/v1/predict/all`
Retourne les prédictions des 3 modèles pour comparer.

```json
{
  "predictions": [
    {"predicted_days": 47, "model_used": "xgboost", ...},
    {"predicted_days": 52, "model_used": "random_forest", ...},
    {"predicted_days": 61, "model_used": "linear_regression", ...}
  ]
}
```

La documentation interactive complète est disponible sur **`/docs`** (Swagger UI).

---

## Pistes d'amélioration

### 1. Feature engineering — impact le plus fort ✅ implémenté

C'est souvent **plus efficace que de changer de modèle**.

#### Ce qu'on a fait : ajout de `price_ratio`

On a ajouté une feature dérivée calculée automatiquement à partir des inputs :

```python
price_ratio = listing_price / (surface × market_price_m2)
```

- `price_ratio = 1.0`  → bien affiché exactement au prix du marché
- `price_ratio = 1.30` → bien surévalué de 30% → restera longtemps sur le marché
- `price_ratio = 0.85` → bien sous-évalué de 15% → se vendra rapidement

Cette feature n'est pas saisie par l'utilisateur — elle est calculée automatiquement dans `predictor.py` à partir des features déjà existantes (`listing_price`, `surface`, `market_price_m2`).

#### Résultats avant / après

```
                      Avant         Après         Gain
──────────────────────────────────────────────────────────
linear_regression     R²=0.37       R²=0.89       +0.52 🚀
random_forest         R²=0.46       R²=0.87       +0.41 🚀
xgboost               R²=0.75       R²=0.89       +0.14
```

#### Pourquoi la régression linéaire a autant progressé

C'est la leçon la plus importante du feature engineering :

> *Un mauvais modèle avec de bonnes features bat un bon modèle avec de mauvaises features.*

Avant, la régression linéaire recevait `listing_price`, `surface` et `market_price_m2` séparément. Elle cherchait une relation du type :
```
days = a×listing_price + b×surface + c×market_price_m2 + ...
```

Mais la vraie relation est `listing_price / (surface × market_price_m2)` — une division et une multiplication que la régression linéaire est **incapable de découvrir seule**. C'est une limitation fondamentale des modèles linéaires.

Avec `price_ratio` directement en entrée, elle peut apprendre :
```
days = a×price_ratio + b×condition + ...
```
C'est exactement la relation codée dans le générateur. Elle l'apprend immédiatement.

#### Pourquoi XGBoost a moins progressé

XGBoost et Random Forest arrivaient déjà à *deviner* approximativement ce ratio en combinant les features entre elles — c'est ce que les arbres de décision font naturellement. L'ajout de `price_ratio` leur confirme ce qu'ils avaient partiellement trouvé, d'où un gain plus modeste.

**Résultat final remarquable : la régression linéaire est maintenant aussi précise que XGBoost** (R²=0.89 pour les deux). La comparaison des trois modèles dans le frontend illustre parfaitement ce phénomène.

D'autres features dérivées envisageables :
```python
price_per_m2  = listing_price / surface      # prix réel affiché au m²
rooms_density = rooms / surface              # densité des pièces (studio vs grande maison)
age_condition = age * condition_encoded      # interaction âge × état
```

**Règle générale :** plus on encode explicitement la connaissance métier dans les features, moins les modèles ont à la deviner — et meilleures sont les performances.

### 2. Hyperparameter tuning — impact moyen

Les modèles utilisent des paramètres raisonnables mais pas optimaux. `GridSearchCV` teste automatiquement toutes les combinaisons :

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    "model__n_estimators":  [100, 200, 300],
    "model__max_depth":     [4, 6, 8],
    "model__learning_rate": [0.01, 0.05, 0.1],
}
search = GridSearchCV(pipeline, param_grid, cv=5, scoring="neg_mean_absolute_error")
search.fit(X_train, y_train)
best_pipeline = search.best_estimator_
```

Le `cv=5` est la **validation croisée à 5 folds** : au lieu d'un seul train/test split, on découpe les données en 5 parties et on évalue 5 fois. Les métriques finales sont plus fiables et moins dépendantes du hasard de la découpe.

### 3. Autres modèles — impact marginal sur données tabulaires

XGBoost est déjà excellent sur les données tabulaires. Les alternatives les plus pertinentes :

| Modèle | Avantage vs XGBoost |
|---|---|
| **LightGBM** | 10x plus rapide à entraîner, précision similaire |
| **CatBoost** | Gère les catégorielles nativement (pas besoin de OneHotEncoder), souvent meilleur sur de vraies données immobilières |
| **Réseau de neurones** | Généralement **pire** que XGBoost sur les données tabulaires — réservé aux images, texte, audio |
| **Stacking** | Combiner les 3 modèles en méta-modèle → gain marginal de ~1-2 points de R² |

### 4. Données réelles — impact maximal

La limite principale du projet actuel est le dataset synthétique. Avec de vraies données :
- Les patterns sont plus complexes et non-linéaires
- Les interactions entre features sont plus riches
- Le modèle apprend des vraies spécificités locales (un quartier précis, une tendance de marché)

Sources de données immobilières gratuites : **DVF (Demandes de Valeurs Foncières)** publiées par le gouvernement français — toutes les transactions immobilières en France depuis 2014.

### 5. Validation croisée temporelle

Dans un vrai contexte, les données ont une dimension temporelle : les transactions de 2024 ne se comportent pas comme celles de 2020. Un split temporel (`TimeSeriesSplit`) est plus réaliste qu'un split aléatoire :

```python
# Au lieu de train_test_split aléatoire :
# → train sur 2020-2023, test sur 2024
# Le modèle est évalué sur le futur, pas sur un échantillon aléatoire du passé.
```

### Gains estimés

```
Amélioration                        Gain estimé sur R²
────────────────────────────────────────────────────────
Feature engineering (price_ratio)   +0.15 à +0.20
Hyperparameter tuning XGBoost       +0.03 à +0.05
Passer à LightGBM / CatBoost        +0.01 à +0.03
Données réelles (DVF)               +0.10 à +0.20  (variable)
Validation croisée temporelle       (mesure plus honnête, pas un gain direct)
```
