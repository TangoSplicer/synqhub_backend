"""Application configuration management."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Application
    app_name: str = "SynQ Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8000"]

    # Database
    database_url: str = "postgresql+asyncpg://synq:synq_password@localhost:5432/synq_db"
    database_echo: bool = False
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 3600

    # Celery
    celery_broker_url: str = "amqp://guest:guest@localhost:5672//"
    celery_result_backend: str = "redis://localhost:6379/1"
    celery_task_serializer: str = "json"
    celery_result_serializer: str = "json"

    # JWT
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_expiration_days: int = 7

    # OAuth2
    oauth2_google_client_id: Optional[str] = None
    oauth2_google_client_secret: Optional[str] = None
    oauth2_github_client_id: Optional[str] = None
    oauth2_github_client_secret: Optional[str] = None

    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]

    # Quantum Backends
    ibmq_api_key: Optional[str] = None
    ionq_api_key: Optional[str] = None
    rigetti_api_key: Optional[str] = None

    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str = "noreply@synq.ai"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Monitoring
    prometheus_enabled: bool = True
    jaeger_enabled: bool = True
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 1000
    rate_limit_period: int = 3600

    # Feature Flags
    enable_qml_service: bool = True
    enable_synthesis_service: bool = False
    enable_transpilation_service: bool = False
    enable_synqhub_registry: bool = False

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()
