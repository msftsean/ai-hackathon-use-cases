"""
Services module for Constituent Services Agent.

Provides factory functions for creating service instances based on
configuration (mock vs. real Azure services).
"""

from typing import TYPE_CHECKING

from src.config.settings import get_settings, is_mock_mode

if TYPE_CHECKING:
    from src.agent.foundry_iq_client import FoundryIQKnowledgeBase
    from src.services.knowledge_service import KnowledgeService


def get_knowledge_base() -> "FoundryIQKnowledgeBase":
    """
    Get knowledge base service instance.

    Returns mock or real Foundry IQ client based on USE_MOCK_SERVICES setting.

    Returns:
        FoundryIQKnowledgeBase: Knowledge base service instance
    """
    if is_mock_mode():
        from src.agent.foundry_iq_client import MockFoundryIQKnowledgeBase
        return MockFoundryIQKnowledgeBase()
    else:
        from src.agent.foundry_iq_client import FoundryIQKnowledgeBase
        settings = get_settings()
        return FoundryIQKnowledgeBase(
            connection_string=settings.azure_ai_project_connection_string
        )


def get_knowledge_service() -> "KnowledgeService":
    """
    Get knowledge service instance.

    Returns:
        KnowledgeService: Service for loading and managing agency content
    """
    from src.services.knowledge_service import KnowledgeService
    return KnowledgeService()


def get_translation_service():
    """
    Get translation service instance.

    Returns mock or real Azure Translator based on USE_MOCK_SERVICES setting.
    """
    if is_mock_mode():
        from src.services.translation_service import MockTranslationService
        return MockTranslationService()
    else:
        from src.services.translation_service import TranslationService
        settings = get_settings()
        return TranslationService(
            key=settings.azure_translator_key,
            endpoint=settings.azure_translator_endpoint,
            region=settings.azure_translator_region,
        )


def get_audit_service():
    """
    Get audit service instance.

    Returns mock or real Cosmos DB audit service based on USE_MOCK_SERVICES setting.
    """
    if is_mock_mode():
        from src.services.audit_service import MockAuditService
        return MockAuditService()
    else:
        from src.services.audit_service import AuditService
        settings = get_settings()
        return AuditService(
            endpoint=settings.cosmos_endpoint,
            key=settings.cosmos_key,
            database=settings.cosmos_database,
        )


__all__ = [
    "get_knowledge_base",
    "get_knowledge_service",
    "get_translation_service",
    "get_audit_service",
]
