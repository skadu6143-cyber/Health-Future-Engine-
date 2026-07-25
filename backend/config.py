import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration, pulled from environment variables."""

    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "health_future_engine")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MIN", "60"))
    )
    JWT_TOKEN_LOCATION = ["headers"]

    # Flask
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
    PORT = int(os.getenv("PORT", "5000"))
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")

    # ML
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml", "risk_model.joblib")
