FROM python:3.11-slim

WORKDIR /app

# Dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code source
COPY . .

# Création du dossier models si absent
RUN mkdir -p models

# Entraînement des modèles à la construction de l'image
# (les modèles sont baked-in, pas de cold start à l'exécution)
RUN python -m scripts.train_models

# Démarrage
# $PORT est injecté dynamiquement par Render en production
# En local Docker, il vaut 8000 (défini dans .env)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
