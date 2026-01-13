"""
Configuration settings for Constituent Services Agent.

Loads configuration from environment variables with sensible defaults
for local development.
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Constituent Services Agent"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, description="Enable debug mode")

    # Feature Flags
    use_mock_services: bool = Field(
        default=True,
        description="Use mock services for offline development"
    )

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=5000, description="Server port")

    # Azure AI Project
    azure_ai_project_connection_string: Optional[str] = Field(
        default=None,
        description="Azure AI Project connection string"
    )

    # Azure OpenAI
    azure_openai_endpoint: Optional[str] = Field(
        default=None,
        description="Azure OpenAI endpoint URL"
    )
    azure_openai_key: Optional[str] = Field(
        default=None,
        description="Azure OpenAI API key"
    )
    azure_openai_deployment: str = Field(
        default="gpt-4",
        description="Azure OpenAI deployment name"
    )

    # Azure Translator
    azure_translator_key: Optional[str] = Field(
        default=None,
        description="Azure Translator API key"
    )
    azure_translator_endpoint: str = Field(
        default="https://api.cognitive.microsofttranslator.com",
        description="Azure Translator endpoint"
    )
    azure_translator_region: str = Field(
        default="eastus",
        description="Azure Translator region"
    )

    # Azure Cosmos DB
    cosmos_endpoint: Optional[str] = Field(
        default=None,
        description="Cosmos DB endpoint URL"
    )
    cosmos_key: Optional[str] = Field(
        default=None,
        description="Cosmos DB access key"
    )
    cosmos_database: str = Field(
        default="constituent-agent",
        description="Cosmos DB database name"
    )

    # Agent Configuration
    confidence_threshold: float = Field(
        default=0.5,
        description="Minimum confidence for response without escalation offer"
    )
    max_citations: int = Field(
        default=5,
        description="Maximum citations to include in response"
    )
    response_timeout_seconds: int = Field(
        default=30,
        description="Maximum time for agent response"
    )

    # Supported Languages (ISO 639-1 codes)
    supported_languages: list[str] = Field(
        default=["en", "es", "zh", "ar", "ru", "ko", "ht", "bn"],
        description="Supported language codes"
    )
    default_language: str = Field(
        default="en",
        description="Default language for responses"
    )

    # Session Management
    session_ttl_seconds: int = Field(
        default=1800,  # 30 minutes
        description="Session time-to-live in seconds"
    )
    conversation_retention_days: int = Field(
        default=30,
        description="Days to retain conversation data"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings loaded from environment.
    """
    return Settings()


def is_mock_mode() -> bool:
    """
    Check if application is running in mock mode.

    Returns:
        bool: True if mock services should be used.
    """
    return get_settings().use_mock_services
