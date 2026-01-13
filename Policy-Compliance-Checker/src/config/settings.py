"""Settings configuration using Pydantic."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment_name: str = "gpt-4"

    # Azure Form Recognizer (optional)
    azure_form_recognizer_endpoint: str = ""
    azure_form_recognizer_key: str = ""

    # Application settings
    flask_port: int = 5000
    use_mock_services: bool = True
    log_level: str = "INFO"
    max_file_size_mb: int = 10

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def has_azure_openai(self) -> bool:
        """Check if Azure OpenAI is configured."""
        return bool(
            self.azure_openai_endpoint
            and self.azure_openai_api_key
            and "your" not in self.azure_openai_api_key.lower()
        )

    @property
    def has_form_recognizer(self) -> bool:
        """Check if Azure Form Recognizer is configured."""
        return bool(
            self.azure_form_recognizer_endpoint
            and self.azure_form_recognizer_key
            and "your" not in self.azure_form_recognizer_key.lower()
        )


# Global settings instance
settings = Settings()
