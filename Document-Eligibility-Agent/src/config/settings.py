"""Application settings using pydantic-settings."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Feature flags
    use_mock_services: bool = Field(default=True, description="Use mock services for development")

    # Azure Document Intelligence
    azure_doc_intelligence_endpoint: Optional[str] = Field(
        default=None, description="Azure Document Intelligence endpoint"
    )
    azure_doc_intelligence_key: Optional[str] = Field(
        default=None, description="Azure Document Intelligence API key"
    )

    # Azure Blob Storage
    azure_storage_connection_string: Optional[str] = Field(
        default=None, description="Azure Storage connection string"
    )
    azure_storage_container: str = Field(
        default="documents", description="Blob container name"
    )

    # Azure Cosmos DB
    cosmos_endpoint: Optional[str] = Field(
        default=None, description="Cosmos DB endpoint"
    )
    cosmos_key: Optional[str] = Field(default=None, description="Cosmos DB key")
    cosmos_database: str = Field(
        default="doc-eligibility", description="Cosmos DB database name"
    )

    # Microsoft Graph
    graph_client_id: Optional[str] = Field(
        default=None, description="Microsoft Graph client ID"
    )
    graph_client_secret: Optional[str] = Field(
        default=None, description="Microsoft Graph client secret"
    )
    graph_tenant_id: Optional[str] = Field(
        default=None, description="Microsoft Graph tenant ID"
    )
    intake_mailbox: str = Field(
        default="intake@agency.ny.gov", description="Email intake mailbox address"
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )

    # Flask
    flask_secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Flask secret key",
    )
    flask_debug: bool = Field(default=True, description="Flask debug mode")
    flask_host: str = Field(default="0.0.0.0", description="Flask host")
    flask_port: int = Field(default=5001, description="Flask port")

    # Processing Configuration
    confidence_threshold: float = Field(
        default=0.85, description="Confidence threshold for auto-approval"
    )
    max_file_size_mb: int = Field(
        default=50, description="Maximum file size in MB"
    )
    document_retention_years: int = Field(
        default=7, description="Document retention period in years"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
