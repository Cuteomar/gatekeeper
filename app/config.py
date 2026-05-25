import os
from dotenv import load_dotenv

# Load .env with override=True to take precedence over system env vars
load_dotenv(override=True)


class Config:
    """Application configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
    # Default to SQLite so the project works out of the box
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///rbac.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    BCRYPT_LOG_ROUNDS = 12