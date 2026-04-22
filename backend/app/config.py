from pydantic_settings import BaseSettings
from pathlib import Path

# Racine du projet (remonte depuis app/config.py)
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    class Config:
        env_file = BASE_DIR / ".env"

settings = Settings() # Instanciation de la classe Settings pour charger les variables d'environnement