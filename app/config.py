# app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Variables obligatoires
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DEBUG: bool = False

    # Variables optionnelles avec valeurs par défaut
    APP_NAME: str = "My Awesome API"
    APP_VERSION: str = "1.0.0"  # Ajoutez cette ligne
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    ALLOW_ORIGINS: list[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list[str] = ["*"]
    ALLOW_HEADERS: list[str] = ["*"]
    PARENT_MEDIA_NAME: str = "medias"
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    ADMIN_MAIL: str

    # Configuration Pydantic
    class Config:
        env_file = ".env"  # Charge les variables depuis le fichier .env à la racine
        extra = "ignore"  # Ignore les variables supplémentaires non définies dans Settings


# Instance globale des paramètres
settings = Settings()