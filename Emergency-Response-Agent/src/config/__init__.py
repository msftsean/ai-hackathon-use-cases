"""Configuration module for Emergency Response Agent."""

import logging
import os

from .settings import Settings

# Configure logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("emergency_response_agent")

__all__ = ["Settings", "logger"]
