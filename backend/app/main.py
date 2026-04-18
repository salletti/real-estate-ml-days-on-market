"""
main.py
-------
Point d'entrée de l'application FastAPI.

Responsabilités :
  - Créer l'instance FastAPI
  - Configurer le middleware CORS
  - Enregistrer les routers
  - Gérer le cycle de vie (démarrage / arrêt) via lifespan
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.dependencies import get_model_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gère le cycle de vie de l'application.

    Le code avant 'yield' s'exécute AU DÉMARRAGE du serveur.
    Le code après 'yield' s'exécute À L'ARRÊT du serveur.

    C'est ici qu'on charge les modèles ML en mémoire — une seule fois,
    avant que le serveur commence à accepter des requêtes.

    Pourquoi dans le lifespan et pas au niveau module :
      Au niveau module, le code s'exécute à l'import — trop tôt.
      Le lifespan garantit que l'environnement est complètement
      initialisé (variables d'env, fichiers disponibles) avant le chargement.
    """
    # --- Démarrage ---
    logger.info("Starting Days on Market API...")
    service = get_model_service()
    service.load(
        model_dir=settings.model_dir,
        default_model=settings.default_model,
    )
    logger.info("API ready.")

    yield  # Le serveur tourne ici et accepte les requêtes

    # --- Arrêt (optionnel) ---
    logger.info("Shutting down.")


# ------------------------------------------------------------------
# Création de l'application FastAPI
# ------------------------------------------------------------------
app = FastAPI(
    title="Days on Market API",
    description="Prédit le temps de vente d'un bien immobilier.",
    version="1.0.0",
    lifespan=lifespan,
)

# ------------------------------------------------------------------
# Middleware CORS
# ------------------------------------------------------------------
# CORS (Cross-Origin Resource Sharing) : par sécurité, les navigateurs
# bloquent les requêtes HTTP vers un domaine différent de celui de la page.
#
# Concrètement : le frontend sur https://ton-app.vercel.app ne peut pas
# appeler https://ton-api.onrender.com sans que le backend l'autorise
# explicitement via ces headers.
#
# En local Docker, nginx proxifie /api → backend (même origine).
# En production, il faut lister l'URL Vercel dans CORS_ORIGINS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE...
    allow_headers=["*"],  # Content-Type, Authorization...
)

# ------------------------------------------------------------------
# Enregistrement des routers
# ------------------------------------------------------------------
# Import ici (et non en haut du fichier) pour éviter les imports
# circulaires : les routes importent les dépendances, qui importent
# le service, etc.
from app.routes import health, models, predict  # noqa: E402

app.include_router(health.router)
app.include_router(predict.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")
