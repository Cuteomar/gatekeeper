import os
from pathlib import Path
from dotenv import load_dotenv

# Always prefer .env if it exists
_dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_dotenv_path, override=True)


class Config:
    """Application configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")

    # Use SQLite for local dev unless DATABASE_URL explicitly points elsewhere
    db_url = os.getenv("DATABASE_URL", "sqlite:///instance/rbac.db")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    BCRYPT_LOG_ROUNDS = 12