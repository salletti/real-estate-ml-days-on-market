"""
registry.py
-----------
Gère la persistance des modèles entraînés : sauvegarde sur disque
et rechargement en mémoire au démarrage de l'API.

Pourquoi ce fichier existe :
  Entraîner un modèle ML prend du temps (quelques secondes à plusieurs
  minutes). On ne peut pas entraîner à chaque démarrage du serveur, ni
  à chaque requête. La solution : entraîner une fois, sauvegarder le
  résultat sur disque, recharger au démarrage.

  Un modèle entraîné = un pipeline sklearn complet (preprocessor + modèle).
  On sauvegarde aussi ses métriques (MAE, RMSE, R²) dans un fichier JSON
  séparé pour pouvoir les afficher dans l'API sans recharger le modèle.

Structure des fichiers générés (dans backend/models/) :
  linear_regression.joblib  ← pipeline sklearn sérialisé (binaire)
  linear_regression.json    ← métriques + métadonnées (texte lisible)
  random_forest.joblib
  random_forest.json
  xgboost.joblib
  xgboost.json
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Responsabilité unique : sauvegarder et charger des modèles ML.

    Cette classe ne sait pas ce qu'est un Random Forest ou un XGBoost —
    elle manipule uniquement des Pipeline sklearn et des dicts de métriques.
    C'est le rôle de trainer.py de créer ces pipelines.
    """

    @staticmethod
    def save(
        name: str,
        pipeline: Pipeline,
        metrics: dict,
        model_dir: str | Path,
    ) -> None:
        """
        Sauvegarde un pipeline entraîné et ses métriques sur le disque.

        Deux fichiers sont créés :
          {name}.joblib  : le pipeline sklearn complet (preprocessor + modèle)
                           Format binaire — non lisible à l'œil nu mais chargeable
                           instantanément avec joblib.load().

          {name}.json    : les métriques et métadonnées au format texte.
                           Permet à l'API de lister les modèles et leurs scores
                           sans charger les fichiers .joblib (qui peuvent être lourds).

        Args:
            name       : identifiant du modèle, ex: "random_forest"
            pipeline   : pipeline sklearn fitté (preprocessor + estimateur)
            metrics    : dict avec les clés "mae", "rmse", "r2", "residual_std"
            model_dir  : dossier de destination, ex: "./models"
        """
        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)

        # --- Sauvegarde du pipeline (format binaire) ---
        # joblib est préféré à pickle pour les objets numpy/sklearn :
        # il est plus rapide et gère mieux les grands tableaux.
        joblib_path = model_dir / f"{name}.joblib"
        joblib.dump(pipeline, joblib_path)
        logger.info(f"Pipeline saved → {joblib_path}")

        # --- Sauvegarde des métadonnées (format JSON lisible) ---
        metadata = {
            "name": name,
            "algorithm": name,  # ex: "random_forest"
            "trained_at": datetime.now(timezone.utc).isoformat(),
            **metrics,          # mae, rmse, r2, residual_std
        }
        json_path = model_dir / f"{name}.json"
        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Metadata saved → {json_path}")

    @staticmethod
    def load_all(model_dir: str | Path) -> dict:
        """
        Charge tous les modèles disponibles depuis le dossier models/.

        Appelé une seule fois au démarrage de l'API (dans model_service.py).
        Après ça, les pipelines sont gardés en mémoire — pas de I/O disque
        à chaque requête.

        Returns:
            Un dict dont les clés sont les noms de modèles :
            {
                "random_forest": {
                    "pipeline": <Pipeline sklearn fitté>,
                    "metadata": {"mae": 8.2, "rmse": 12.1, "r2": 0.81, ...}
                },
                "xgboost": { ... },
                "linear_regression": { ... },
            }

        Comportement si un fichier est corrompu ou manquant :
            Le modèle est ignoré avec un warning — les autres sont chargés.
            L'API ne crashe pas si un seul modèle est défaillant.
        """
        model_dir = Path(model_dir)
        registry = {}

        # On itère sur tous les fichiers .json du dossier
        # (chaque .json correspond à un modèle entraîné)
        json_files = list(model_dir.glob("*.json"))

        if not json_files:
            logger.warning(f"No models found in {model_dir}. Run train_models.py first.")
            return registry

        for json_path in sorted(json_files):
            name = json_path.stem  # ex: "random_forest" (sans extension)
            joblib_path = json_path.with_suffix(".joblib")

            # Vérification que le .joblib correspondant existe
            if not joblib_path.exists():
                logger.warning(f"Missing .joblib for '{name}', skipping.")
                continue

            try:
                with open(json_path) as f:
                    metadata = json.load(f)

                pipeline = joblib.load(joblib_path)

                registry[name] = {
                    "pipeline": pipeline,
                    "metadata": metadata,
                }
                logger.info(f"Loaded model '{name}' (MAE={metadata.get('mae', '?'):.2f})")

            except Exception as e:
                # On ne fait pas crasher tout le serveur pour un seul modèle corrompu
                logger.error(f"Failed to load model '{name}': {e}")
                continue

        return registry

    @staticmethod
    def get_best_model(registry: dict) -> str | None:
        """
        Retourne le nom du modèle avec la MAE la plus basse.

        La MAE (Mean Absolute Error) est la métrique principale de sélection :
        elle représente l'erreur moyenne en jours — facile à interpréter.
        Un modèle avec MAE=8 se trompe en moyenne de 8 jours.

        Returns None si le registry est vide (cas où aucun modèle n'a été trouvé).
        """
        if not registry:
            return None

        best = min(
            registry.keys(),
            key=lambda name: registry[name]["metadata"].get("mae", float("inf")),
        )
        logger.info(f"Best model by MAE: '{best}'")
        return best
