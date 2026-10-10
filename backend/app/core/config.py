"""
Application configuration loaded from environment variables / .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        # Suppress the pydantic warning about field names starting with "model_"
        protected_namespaces=("settings_",),
    )

    # Server
    backend_port: int = 8000

    # CORS -- accepts a comma-separated string like "http://localhost:5173"
    cors_origins: list[str] = [
    "http://localhost:5173",
    "https://aquapura-frontend.onrender.com",
]

    # Database
    database_url: str = "sqlite:///./aquapura.db"

    # ML model artifact path (relative to the project root).
    # The model_loader service uses its own path resolution; this setting
    # is kept for potential future use (e.g. multiple model variants).
    model_path: str = "../ml/models/water_quality_model.joblib"

    # JWT authentication
    # Override jwt_secret_key via a .env file or environment variable.
    # Never commit a real secret to source control.
    jwt_secret_key:     str = "change_me_before_production"
    jwt_algorithm:      str = "HS256"
    jwt_expire_minutes: int = 60


settings = Settings()
