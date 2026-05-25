import os
from dotenv import load_dotenv

# Load .env with override=True to take precedence over system env vars
load_dotenv(override=True)


class Config:
    """Application configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")

    # Render / Railway / Heroku provide DATABASE_URL with postgres://
    db_url = os.getenv("DATABASE_URL", "sqlite:///rbac.db")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    BCRYPT_LOG_ROUNDS = 12