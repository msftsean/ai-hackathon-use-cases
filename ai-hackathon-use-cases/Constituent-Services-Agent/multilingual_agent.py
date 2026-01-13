"""Multi-language support for constituent services"""
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential


class MultilingualAgent:
    """Wrapper for multi-language constituent interactions"""

    SUPPORTED_LANGUAGES = ["en", "es", "zh", "ar", "ru", "ko", "ht", "bn"]

    LANGUAGE_NAMES = {
        "en": "English",
        "es": "Spanish",
        "zh": "Chinese",
        "ar": "Arabic",
        "ru": "Russian",
        "ko": "Korean",
        "ht": "Haitian Creole",
        "bn": "Bengali"
    }

    def __init__(self, translator_key: str, translator_endpoint: str):
        self.translator = TextTranslationClient(
            endpoint=translator_endpoint,
            credential=AzureKeyCredential(translator_key)
        )

    def detect_and_translate(self, text: str) -> tuple[str, str]:
        """Detect language and translate to English for processing"""
        detection = self.translator.detect_language([text])
        detected_lang = detection[0].language

        if detected_lang != "en":
            translation = self.translator.translate(
                content=[text],
                to=["en"],
                from_=detected_lang
            )
            return translation[0].translations[0].text, detected_lang
        return text, "en"

    def translate_response(self, text: str, target_lang: str) -> str:
        """Translate response back to user's language"""
        if target_lang == "en":
            return text
        translation = self.translator.translate(
            content=[text],
            to=[target_lang]
        )
        return translation[0].translations[0].text


class MockMultilingualAgent:
    """Mock implementation for offline development"""

    SUPPORTED_LANGUAGES = ["en", "es", "zh", "ar", "ru", "ko", "ht", "bn"]

    LANGUAGE_NAMES = {
        "en": "English",
        "es": "Spanish",
        "zh": "Chinese",
        "ar": "Arabic",
        "ru": "Russian",
        "ko": "Korean",
        "ht": "Haitian Creole",
        "bn": "Bengali"
    }

    # Simple mock translations for demo purposes
    MOCK_TRANSLATIONS = {
        "es": {
            "hello": "hola",
            "How do I apply for SNAP benefits?": "Como puedo solicitar beneficios de SNAP?"
        },
        "zh": {
            "hello": "你好",
            "How do I apply for SNAP benefits?": "如何申请SNAP福利？"
        }
    }

    def __init__(self, translator_key: str = None, translator_endpoint: str = None):
        pass

    def detect_and_translate(self, text: str) -> tuple[str, str]:
        """Mock language detection - assumes English for demo"""
        # Check for common non-English phrases
        if text.startswith("hola") or "como" in text.lower():
            return "How do I apply for SNAP benefits?", "es"
        if any(ord(c) > 127 for c in text):  # Simple check for non-ASCII
            return text, "zh"
        return text, "en"

    def translate_response(self, text: str, target_lang: str) -> str:
        """Mock translation - returns original text with language note"""
        if target_lang == "en":
            return text
        return f"[{self.LANGUAGE_NAMES.get(target_lang, target_lang)}] {text}"
