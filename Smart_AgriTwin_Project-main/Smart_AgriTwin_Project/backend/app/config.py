import os
from datetime import timedelta
class Config:
    # Database settings loaded from .env
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "Smart_AgriTwin_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "123456")
    # TOKEN EXPIRE süresini 1 güne çıkardık
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    # SQLAlchemy PostgreSQL connection
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-change-me")
    TELEMETRY_RETENTION_DAYS = int(os.getenv("TELEMETRY_RETENTION_DAYS", "30"))
