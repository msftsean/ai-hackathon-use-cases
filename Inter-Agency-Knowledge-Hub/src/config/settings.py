"""Configuration settings for Inter-Agency Knowledge Hub."""

import logging
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Azure AI Search Configuration
    azure_search_endpoint: str = Field(
        default="https://mock-search.search.windows.net",
        description="Azure AI Search endpoint URL",
    )
    azure_search_api_key: str = Field(
        default="mock-api-key",
        description="Azure AI Search API key",
    )
    azure_search_index_prefix: str = Field(
        default="agency-docs",
        description="Prefix for agency document indexes",
    )

    # Azure OpenAI Configuration
    azure_openai_endpoint: str = Field(
        default="https://mock-openai.openai.azure.com/",
        description="Azure OpenAI endpoint URL",
    )
    azure_openai_api_key: str = Field(
        default="mock-openai-key",
        description="Azure OpenAI API key",
    )
    azure_openai_deployment_name: str = Field(
        default="gpt-4",
        description="Azure OpenAI deployment name",
    )
    azure_openai_embedding_deployment: str = Field(
        default="text-embedding-ada-002",
        description="Azure OpenAI embedding deployment name",
    )

    # Microsoft Entra ID Configuration
    azure_tenant_id: str = Field(
        default="mock-tenant-id",
        description="Azure AD tenant ID",
    )
    azure_client_id: str = Field(
        default="mock-client-id",
        description="Azure AD client ID",
    )
    azure_client_secret: str = Field(
        default="mock-client-secret",
        description="Azure AD client secret",
    )

    # Application Settings
    use_mock_services: bool = Field(
        default=True,
        description="Use mock services for offline development",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    secret_key: str = Field(
        default="change-this-in-production",
        description="Flask secret key",
    )

    # Server Configuration
    flask_host: str = Field(default="0.0.0.0", description="Flask host")
    flask_port: int = Field(default=5000, description="Flask port")

    # Database Configuration
    database_path: str = Field(
        default="./data/audit.db",
        description="SQLite database path",
    )

    # Cache Settings
    permission_cache_ttl_minutes: int = Field(
        default=15,
        description="Permission cache TTL in minutes",
    )
    search_cache_ttl_seconds: int = Field(
        default=300,
        description="Search cache TTL in seconds",
    )

    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60,
        description="Rate limit per minute per user",
    )
    rate_limit_per_hour: int = Field(
        default=1000,
        description="Rate limit per hour per user",
    )

    # Cross-Reference Settings
    cross_ref_min_confidence: float = Field(
        default=0.7,
        description="Minimum confidence threshold for cross-references",
    )
    cross_ref_max_results: int = Field(
        default=10,
        description="Maximum cross-reference results",
    )

    # Review Settings
    review_criteria_path: str = Field(
        default="./assets/review_criteria.json",
        description="Path to review criteria configuration",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @property
    def database_dir(self) -> Path:
        """Get the database directory path."""
        return Path(self.database_path).parent

    def setup_logging(self) -> logging.Logger:
        """Configure and return the application logger."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        return logging.getLogger("knowledge_hub")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global logger instance
logger = get_settings().setup_logging()
