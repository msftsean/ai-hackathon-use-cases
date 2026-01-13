# NYC Citizen Assistant Configuration Settings

import os
import secrets

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is not installed - will use system environment variables only
    pass
except Exception:
    # .env file might not exist or have issues, which is okay
    pass

def _safe_int_conversion(value, default):
    """Safely convert string to int with fallback to default."""
    try:
        return int(value) if value else default
    except (ValueError, TypeError):
        return default

class Config:
    """Application configuration class."""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")
    
    # Azure AI Search Configuration
    AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
    AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
    AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "city-services")
    
    # Application Settings
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # City API Settings (for mock services)
    CITY_API_BASE_URL = os.getenv("CITY_API_BASE_URL", "https://api.nyc.gov")
    CITY_API_KEY = os.getenv("CITY_API_KEY")
    
    # Application Settings with safe conversion
    PORT = _safe_int_conversion(os.getenv("PORT"), 5000)
    
    # Conversation Settings with safe conversion
    MAX_CONVERSATION_HISTORY = _safe_int_conversion(os.getenv("MAX_CONVERSATION_HISTORY"), 10)
    MAX_SEARCH_RESULTS = _safe_int_conversion(os.getenv("MAX_SEARCH_RESULTS"), 3)
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration settings."""
        required_settings = [
            ("AZURE_OPENAI_ENDPOINT", cls.AZURE_OPENAI_ENDPOINT),
            ("AZURE_OPENAI_API_KEY", cls.AZURE_OPENAI_API_KEY),
            ("AZURE_SEARCH_ENDPOINT", cls.AZURE_SEARCH_ENDPOINT),
            ("AZURE_SEARCH_KEY", cls.AZURE_SEARCH_KEY)
        ]
        
        missing_settings = []
        for setting_name, setting_value in required_settings:
            if not setting_value:
                missing_settings.append(setting_name)
        
        if missing_settings:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_settings)}")
        
        return True
    
    @classmethod
    def is_configured(cls):
        """Check if all required settings are available without raising an exception."""
        try:
            cls.validate_config()
            return True
        except ValueError:
            return False
    
    @classmethod
    def get_missing_settings(cls):
        """Get list of missing required settings."""
        required_settings = [
            ("AZURE_OPENAI_ENDPOINT", cls.AZURE_OPENAI_ENDPOINT),
            ("AZURE_OPENAI_API_KEY", cls.AZURE_OPENAI_API_KEY),
            ("AZURE_SEARCH_ENDPOINT", cls.AZURE_SEARCH_ENDPOINT),
            ("AZURE_SEARCH_KEY", cls.AZURE_SEARCH_KEY)
        ]
        
        missing_settings = []
        for setting_name, setting_value in required_settings:
            if not setting_value:
                missing_settings.append(setting_name)
        
        return missing_settings

# Note: Configuration validation is not called at import time
# Call Config.validate_config() explicitly when needed in your application