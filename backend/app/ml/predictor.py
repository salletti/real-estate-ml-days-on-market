"""
predictor.py
------------
Logique d'inférence : transforme les données brutes d'un bien immobilier
en une prédiction de days_on_market avec un intervalle de confiance.

Responsabilité unique : prendre un dict de features + un pipeline fitté
et retourner un résultat structuré. Aucune connaissance de FastAPI ici.

Pourquoi un intervalle de confiance ?
  Retourner "47 jours" seul est trompeur. Tous les modèles se trompent.
  Retourner "entre 30 et 65 jours" est plus honnête et plus utile pour
  l'utilisateur. On utilise le residual_std calculé à l'entraînement
  (écart-type des erreurs sur le test set) pour estimer cet intervalle.

  Formule : intervalle à 95% = prédiction ± 1.96 × residual_std
  Cela signifie : "dans 95% des cas, la vraie valeur sera dans cet intervalle"
  (sous hypothèse que les erreurs suivent une distribution normale).

Stratégie par modèle :
  - Random Forest  : variance inter-arbres (incertitude native du modèle)
  - XGBoost        : residual_std stocké dans les métadonnées à l'entraînement
  - Linear Reg.    : residual_std stocké dans les métadonnées à l'entraînement
"""

from typing import Any

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from app.ml.constants import FEATURE_COLUMNS


def predict(
    features: dict[str, Any],
    pipeline: Pipeline,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """
    Effectue une prédiction pour un bien immobilier.

    Args:
        features : dict contenant les 17 features du bien
                   ex: {"surface": 80, "city": "Paris", "energy_rating": "C", ...}
        pipeline : pipeline sklearn fitté (preprocessor + modèle)
        metadata : métadonnées du modèle (contient residual_std, algorithm, métriques)

    Returns:
        {
            "predicted_days": 47,
            "lower_bound": 28,
            "upper_bound": 66,
            "model_used": "xgboost",
            "model_metrics": {"mae": 15.42, "rmse": 19.40, "r2": 0.7460}
        }
    """

    # ------------------------------------------------------------------
    # 1. Calcul des features dérivées
    # ------------------------------------------------------------------
    # price_ratio n'est pas envoyé par l'utilisateur — il est calculé
    # automatiquement à partir des features brutes reçues par l'API.
    # On copie le dict pour ne pas modifier l'original (bonne pratique).
    features = dict(features)
    features["price_ratio"] = features["listing_price"] / (
        features["surface"] * features["market_price_m2"]
    )

    # ------------------------------------------------------------------
    # 2. Construction du DataFrame avec l'ordre exact des colonnes
    # ------------------------------------------------------------------
    # C'est l'étape la plus critique de l'inférence.
    # Le ColumnTransformer a été fitté avec les colonnes dans l'ordre
    # défini par FEATURE_COLUMNS. Si on lui envoie les colonnes dans
    # un ordre différent, il appliquera les mauvaises transformations
    # sur les mauvaises colonnes — silencieusement.
    #
    # Ex: si "surface" arrive à la position où le modèle attend "age",
    # il va normaliser la surface comme si c'était un âge → prédiction absurde.
    #
    # [features] → liste d'un seul dict = DataFrame d'une ligne
    # [FEATURE_COLUMNS] → force l'ordre des colonnes
    df = pd.DataFrame([features])[FEATURE_COLUMNS]

    # ------------------------------------------------------------------
    # 2. Prédiction brute via le pipeline complet
    # ------------------------------------------------------------------
    # pipeline.predict() fait en interne :
    #   1. preprocessor.transform(df)  ← applique StandardScaler, OrdinalEncoder, etc.
    #   2. model.predict(df_transformed) ← prédit days_on_market
    #
    # On obtient un array numpy d'une valeur (ex: array([47.3]))
    # On prend [0] pour extraire le float.
    raw_prediction = float(pipeline.predict(df)[0])

    # On arrondit au jour entier — les jours fractionnaires n'ont pas de sens
    predicted_days = max(1, int(round(raw_prediction)))

    # ------------------------------------------------------------------
    # 3. Calcul de l'intervalle de confiance
    # ------------------------------------------------------------------
    lower, upper = _compute_confidence_interval(
        df=df,
        pipeline=pipeline,
        metadata=metadata,
        predicted_days=predicted_days,
    )

    # ------------------------------------------------------------------
    # 4. Construction du résultat
    # ------------------------------------------------------------------
    return {
        "predicted_days": predicted_days,
        "lower_bound": lower,
        "upper_bound": upper,
        "model_used": metadata.get("name", "unknown"),
        "model_metrics": {
            "mae": metadata.get("mae"),
            "rmse": metadata.get("rmse"),
            "r2": metadata.get("r2"),
        },
    }


def _compute_confidence_interval(
    df: pd.DataFrame,
    pipeline: Pipeline,
    metadata: dict[str, Any],
    predicted_days: int,
) -> tuple[int, int]:
    """
    Calcule l'intervalle de confiance à 95% selon le type de modèle.

    Pour Random Forest : on exploite la variance entre les arbres individuels.
      Chaque arbre prédit indépendamment. La dispersion de ces prédictions
      reflète l'incertitude du modèle sur ce bien précis.

    Pour les autres modèles (XGBoost, Linear Regression) : on utilise le
      residual_std calculé sur le test set lors de l'entraînement.
      C'est une approximation globale (même intervalle pour tous les biens)
      mais simple et honnête.
    """
    algorithm = metadata.get("algorithm", "")

    if algorithm == "random_forest":
        std = _rf_prediction_std(df, pipeline)
    else:
        # residual_std est sauvegardé dans le .json lors de l'entraînement
        std = float(metadata.get("residual_std", 15.0))

    # Intervalle à 95% : ± 1.96 × écart-type
    # 1.96 est le z-score correspondant à 95% sous distribution normale
    margin = int(round(1.96 * std))

    lower = max(1, predicted_days - margin)
    upper = predicted_days + margin

    return lower, upper


def _rf_prediction_std(df: pd.DataFrame, pipeline: Pipeline) -> float:
    """
    Calcule l'écart-type des prédictions des arbres individuels
    d'un Random Forest.

    Fonctionnement :
      1. On récupère le preprocessor fitté depuis le pipeline
      2. On transforme df une seule fois (évite de le refaire pour chaque arbre)
      3. On collecte la prédiction de chacun des 200 arbres
      4. L'écart-type de ces 200 prédictions = mesure de l'incertitude

    Plus les arbres sont en désaccord → std élevé → intervalle large.
    Plus les arbres convergent → std faible → intervalle étroit.
    """
    try:
        # Récupération du preprocessor (étape "preprocessor" du Pipeline)
        preprocessor = pipeline.named_steps["preprocessor"]
        # Transformation des données brutes → features numériques
        X_transformed = preprocessor.transform(df)

        # Récupération du RandomForestRegressor (étape "model" du Pipeline)
        rf_model = pipeline.named_steps["model"]

        # Collecte des prédictions de chaque arbre
        # estimators_ = liste des DecisionTreeRegressor individuels
        tree_predictions = np.array(
            [tree.predict(X_transformed)[0] for tree in rf_model.estimators_]
        )

        return float(np.std(tree_predictions))

    except Exception:
        # Fallback si quelque chose ne va pas (ex: modèle non-RF utilisé ici)
        return 15.0
