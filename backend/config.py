import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Core ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # --- Database ---
    # Render/Heroku-style Postgres URLs sometimes start with 'postgres://'
    # SQLAlchemy 1.4+ requires 'postgresql://'
    _raw_db_url = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_code_review"
    )
    if _raw_db_url.startswith("postgres://"):
        _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # --- JWT ---
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_TOKEN_LOCATION = ["headers"]

    # --- CORS ---
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")

    # --- OpenAI ---
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "llama-3.1-8b-instant")
    OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "") or None

    # --- File Upload ---
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    REPORTS_FOLDER = os.path.join(basedir, "reports")
    MAX_CONTENT_LENGTH = 15 * 1024 * 1024  # 15 MB per upload
    ALLOWED_EXTENSIONS = {"py", "zip"}

    # --- Scoring weights (used by utils/scoring.py) ---
    SEVERITY_WEIGHTS = {
        "critical": 25,
        "high": 15,
        "medium": 7,
        "low": 3,
        "info": 1,
    }


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
