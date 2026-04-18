"""
train_models.py
---------------
Point d'entrée CLI pour entraîner les trois modèles ML et les sauvegarder.

Ce script est exécuté :
  - En local : `python -m scripts.train_models` (depuis backend/)
  - Dans Docker : via `RUN python -m scripts.train_models` dans le Dockerfile
    (les modèles sont baked-in dans l'image, pas de cold start au démarrage)

Ce script ne contient pas de logique ML — il orchestre uniquement :
  1. Génération du dataset synthétique
  2. Entraînement via trainer.train_all()
  3. Affichage d'un tableau de comparaison des résultats
"""

import logging
import os
import sys
import warnings

# Le OneHotEncoder peut rencontrer des catégories inconnues sur le test set
# (ex: un zipcode présent dans le test mais pas dans le train). Ce comportement
# est géré explicitement via handle_unknown="ignore" dans preprocessor.py.
# On supprime le warning car il est attendu et traité.
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# Permet d'importer les modules app.* depuis n'importe où
# (nécessaire quand on lance le script en dehors du package)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.data_generator import generate_dataset
from app.ml.trainer import train_all
from app.ml.registry import ModelRegistry

# Configuration du logging : affiche l'heure, le niveau et le message
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    model_dir = os.environ.get("MODEL_DIR", "./models")

    logger.info("=" * 55)
    logger.info("  Days on Market — Model Training Pipeline")
    logger.info("=" * 55)

    # ------------------------------------------------------------------
    # 1. Génération du dataset synthétique
    # ------------------------------------------------------------------
    # 5000 biens immobiliers avec des relations réalistes entre features
    # et days_on_market. Seed fixé pour la reproductibilité.
    logger.info("Generating synthetic dataset (n=5000)...")
    df = generate_dataset(n_samples=5000, seed=42)
    logger.info(f"Dataset ready: {df.shape[0]} rows × {df.shape[1]} columns")
    logger.info(f"Target stats: mean={df['days_on_market'].mean():.1f} days, "
                f"std={df['days_on_market'].std():.1f}, "
                f"min={df['days_on_market'].min()}, "
                f"max={df['days_on_market'].max()}")

    # ------------------------------------------------------------------
    # 2. Entraînement des trois modèles
    # ------------------------------------------------------------------
    # train_all() gère en interne : train/test split, Pipeline, fit,
    # évaluation et sauvegarde via ModelRegistry.
    logger.info(f"\nSaving models to: {model_dir}")
    results = train_all(df, model_dir=model_dir)

    # ------------------------------------------------------------------
    # 3. Tableau de comparaison des résultats
    # ------------------------------------------------------------------
    # Affiche les métriques de chaque modèle côte à côte pour comparer.
    print("\n" + "=" * 55)
    print(f"  {'Model':<22} {'MAE':>6}  {'RMSE':>7}  {'R²':>7}")
    print("=" * 55)

    for name, metrics in results.items():
        print(
            f"  {name:<22} "
            f"{metrics['mae']:>6.2f}  "
            f"{metrics['rmse']:>7.2f}  "
            f"{metrics['r2']:>7.4f}"
        )

    print("=" * 55)

    # ------------------------------------------------------------------
    # 4. Sélection automatique du meilleur modèle
    # ------------------------------------------------------------------
    # On recharge le registry depuis le disque pour simuler ce que
    # fera l'API au démarrage — et vérifier que la sauvegarde fonctionne.
    registry = ModelRegistry.load_all(model_dir)
    best = ModelRegistry.get_best_model(registry)
    print(f"\n  Best model (lowest MAE): {best}")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
