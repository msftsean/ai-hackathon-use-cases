"""Configuration module for Policy Compliance Checker."""

import logging
import os

from .settings import Settings

# Configure logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("policy_compliance_checker")

__all__ = ["Settings", "logger"]
