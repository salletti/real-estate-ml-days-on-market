"""
trainer.py
----------
Orchestre l'entraînement complet des trois modèles ML :
  1. Charge le dataset
  2. Sépare features / target
  3. Découpe en train set et test set
  4. Construit un Pipeline (preprocessor + modèle) pour chacun
  5. Entraîne chaque pipeline sur le train set
  6. Évalue sur le test set (MAE, RMSE, R²)
  7. Sauvegarde via ModelRegistry

Pourquoi un Pipeline sklearn et pas des étapes séparées :
  Sans Pipeline, il faudrait appliquer le preprocessor manuellement avant
  chaque fit() et chaque predict(). Le risque : oublier une étape, ou
  appliquer une transformation dans le mauvais ordre.

  Avec Pipeline, preprocessor + modèle forment un seul objet. Un seul
  .fit(), un seul .predict(). C'est aussi ce qui est sauvegardé en entier
  dans le .joblib — à l'inférence, on donne des données brutes au pipeline
  et il gère tout lui-même.

  pipeline.fit(X_train, y_train) fait en séquence :
    1. preprocessor.fit_transform(X_train)  ← apprend les paramètres de transformation
    2. model.fit(X_train_transformed, y_train)  ← entraîne le modèle

  pipeline.predict(X) fait en séquence :
    1. preprocessor.transform(X)  ← applique (sans ré-apprendre)
    2. model.predict(X_transformed)
"""

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from app.ml.constants import FEATURE_COLUMNS, TARGET
from app.ml.preprocessor import build_preprocessor
from app.ml.registry import ModelRegistry

logger = logging.getLogger(__name__)


def train_all(df: pd.DataFrame, model_dir: str = "./models") -> dict[str, Any]:
    """
    Entraîne les trois modèles, les évalue et les sauvegarde.

    Args:
        df        : DataFrame complet issu de data_generator.generate_dataset()
        model_dir : dossier où sauvegarder les .joblib et .json

    Returns:
        Un dict avec les résultats de chaque modèle :
        {
            "linear_regression": {"mae": 14.2, "rmse": 19.8, "r2": 0.63},
            "random_forest":     {"mae": 8.1,  "rmse": 12.3, "r2": 0.84},
            "xgboost":           {"mae": 7.4,  "rmse": 11.1, "r2": 0.87},
        }
    """

    # ------------------------------------------------------------------
    # 1. Séparation features / target
    # ------------------------------------------------------------------
    # X contient les 17 colonnes d'entrée, dans l'ordre défini par FEATURE_COLUMNS.
    # y contient la colonne cible : days_on_market (un entier par bien).
    X = df[FEATURE_COLUMNS]
    y = df[TARGET]

    # ------------------------------------------------------------------
    # 2. Découpe train / test (80% / 20%)
    # ------------------------------------------------------------------
    # Règle fondamentale : le modèle ne doit JAMAIS voir les données de test
    # pendant l'entraînement. Sinon les métriques seraient trop optimistes
    # et ne refléteraient pas les vraies performances sur des données nouvelles.
    #
    # random_state=42 : fixe le hasard pour que la découpe soit identique
    # à chaque exécution (reproductibilité).
    #
    # shuffle=True (défaut) : mélange les données avant de couper.
    # Important car notre générateur produit les biens dans un ordre non aléatoire.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info(f"Train: {len(X_train)} samples | Test: {len(X_test)} samples")

    # ------------------------------------------------------------------
    # 3. Définition des trois modèles à comparer
    # ------------------------------------------------------------------
    # Chaque entrée est un tuple (nom, estimateur sklearn).
    # On utilise des hyperparamètres raisonnables — ni trop simples (underfitting),
    # ni trop complexes (overfitting).
    models = [
        (
            "linear_regression",
            # Modèle de référence (baseline). Simple, rapide, interprétable.
            # Suppose une relation LINÉAIRE entre les features et la target.
            # Utile pour comprendre si le problème est linéairement séparable,
            # mais souvent battu par les modèles à base d'arbres sur données tabulaires.
            LinearRegression(),
        ),
        (
            "random_forest",
            # Ensemble de 200 arbres de décision entraînés en parallèle sur des
            # sous-ensembles aléatoires des données (bagging). La prédiction finale
            # est la moyenne des 200 arbres → réduit la variance, robuste au bruit.
            #
            # n_estimators=200 : 200 arbres. Plus = meilleur mais plus lent.
            # max_features="sqrt" (défaut) : chaque arbre voit √17 ≈ 4 features
            #   choisies aléatoirement → diversité entre les arbres.
            # n_jobs=-1 : utilise tous les cœurs CPU disponibles.
            RandomForestRegressor(
                n_estimators=200,
                random_state=42,
                n_jobs=-1,
            ),
        ),
        (
            "xgboost",
            # Gradient boosting : les arbres sont construits SÉQUENTIELLEMENT.
            # Chaque nouvel arbre corrige les erreurs résiduelles du précédent.
            # Résultat : très précis sur les données tabulaires, souvent meilleur
            # que Random Forest au prix d'un tuning plus délicat.
            #
            # n_estimators=300     : 300 arbres séquentiels
            # learning_rate=0.05   : contribution faible par arbre (évite l'overfitting)
            # max_depth=6          : profondeur max des arbres (biais/variance)
            # subsample=0.8        : chaque arbre utilise 80% des données
            # colsample_bytree=0.8 : chaque arbre utilise 80% des features
            XGBRegressor(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=6,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
                verbosity=0,  # silence les logs XGBoost
            ),
        ),
    ]

    # ------------------------------------------------------------------
    # 4. Boucle d'entraînement, évaluation et sauvegarde
    # ------------------------------------------------------------------
    results = {}

    for name, estimator in models:
        logger.info(f"Training '{name}'...")

        # Construction du Pipeline : preprocessor → modèle
        # Le preprocessor est reconstruit pour chaque modèle : chaque pipeline
        # a sa propre instance fittée (évite les effets de bord entre modèles).
        pipeline = Pipeline(
            [
                ("preprocessor", build_preprocessor()),
                ("model", estimator),
            ]
        )

        # .fit() entraîne le preprocessor ET le modèle en une seule commande
        pipeline.fit(X_train, y_train)

        # .predict() applique le preprocessor transformé, puis prédit
        y_pred = pipeline.predict(X_test)

        # --------------------------------------------------------------
        # Calcul des métriques sur le test set
        # --------------------------------------------------------------
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        # residual_std : écart-type des erreurs sur le test set.
        # Utilisé dans predictor.py pour estimer l'intervalle de confiance
        # des modèles qui n'ont pas de mécanisme natif (XGBoost, LinearRegression).
        # Ex: si residual_std=10, l'intervalle à 95% sera ± 1.96 × 10 ≈ ± 20 jours.
        residual_std = float(np.std(y_test.values - y_pred))

        metrics = {
            "mae": round(float(mae), 2),
            "rmse": round(float(rmse), 2),
            "r2": round(float(r2), 4),
            "residual_std": round(residual_std, 2),
        }

        logger.info(
            f"  MAE={metrics['mae']:.2f}  "
            f"RMSE={metrics['rmse']:.2f}  "
            f"R²={metrics['r2']:.4f}"
        )

        # Sauvegarde du pipeline fitté + métriques sur le disque
        ModelRegistry.save(
            name=name,
            pipeline=pipeline,
            metrics=metrics,
            model_dir=model_dir,
        )

        results[name] = metrics

    # ------------------------------------------------------------------
    # 5. Modèles quantile pour XGBoost (intervalles de confiance per-property)
    # ------------------------------------------------------------------
    # Ces deux modèles ne prédisent pas la valeur centrale mais directement :
    #   - xgboost_q10 : le 10e percentile (borne basse de la fourchette)
    #   - xgboost_q90 : le 90e percentile (borne haute de la fourchette)
    #
    # Un bien "facile" (typique, bien pricé) → les deux modèles convergent
    #   → fourchette étroite (ex: [24, 33]).
    # Un bien atypique (surévalué, état très mauvais) → ils divergent
    #   → fourchette large mais HONNÊTE (ex: [10, 70]).
    #
    # La "pinball loss" est la métrique de qualité pour les modèles quantile.
    # Pour alpha=0.10 : on veut que 10% des vraies valeurs soient EN DESSOUS
    # de la prédiction. Si c'est bien calibré → pinball loss minimisée.
    #
    # Ces modèles sont "internal=True" : ils ne s'affichent pas dans l'API
    # comme des modèles à part entière — ils servent uniquement à calculer
    # les CI du modèle xgboost principal.
    quantile_configs = [("xgboost_q10", 0.10), ("xgboost_q90", 0.90)]

    for name, alpha in quantile_configs:
        logger.info(f"Training quantile model '{name}' (alpha={alpha})...")

        pipeline = Pipeline(
            [
                ("preprocessor", build_preprocessor()),
                (
                    "model",
                    XGBRegressor(
                        n_estimators=300,
                        learning_rate=0.05,
                        max_depth=6,
                        subsample=0.8,
                        colsample_bytree=0.8,
                        random_state=42,
                        n_jobs=-1,
                        verbosity=0,
                        objective="reg:quantileerror",
                        quantile_alpha=alpha,
                    ),
                ),
            ]
        )

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        # Pinball loss : métrique officielle des modèles quantile.
        # Formule : mean(max(alpha*(y-yhat), (alpha-1)*(y-yhat)))
        errors = y_test.values - y_pred
        pinball = float(np.mean(np.maximum(alpha * errors, (alpha - 1) * errors)))

        metrics = {
            "mae": round(float(mean_absolute_error(y_test, y_pred)), 2),
            "pinball_loss": round(pinball, 4),
            "quantile_alpha": alpha,
            "internal": True,
        }
        logger.info(f"  Pinball loss={metrics['pinball_loss']:.4f}")

        ModelRegistry.save(
            name=name,
            pipeline=pipeline,
            metrics=metrics,
            model_dir=model_dir,
        )

    return results
