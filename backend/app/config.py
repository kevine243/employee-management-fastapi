from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    FRONTEND_URL: str = "http://localhost:5173"

    # Email
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 2525
    MAIL_SERVER: str = "sandbox.smtp.mailtrap.io"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
    }

settings = Settings()  # type: ignore