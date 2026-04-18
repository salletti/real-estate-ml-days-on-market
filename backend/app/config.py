"""
config.py
---------
Centralise toute la configuration de l'application.

Utilise pydantic-settings : les valeurs sont lues automatiquement
depuis les variables d'environnement (ou le fichier .env).

Avantage : un seul endroit pour tous les paramètres.
Si on veut changer le modèle par défaut ou les origines CORS autorisées,
on modifie .env — pas le code.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Renommé ml_model_dir pour éviter le conflit avec le namespace "model_"
    # de Pydantic v2 (model_validate, model_dump, etc. sont réservés).
    ml_model_dir: str = "./models"

    default_model: str = "xgboost"

    cors_origins: str = "http://localhost:3000"

    @property
    def model_dir(self) -> str:
        """Alias pour la compatibilité avec le reste du code."""
        return self.ml_model_dir

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Pydantic v2 : model_config remplace l'ancienne classe Config
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        protected_namespaces=("settings_",),  # désactive le conflit "model_"
    )


# Instance unique importée partout dans l'application
settings = Settings()
