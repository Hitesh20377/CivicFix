import langdetect
from langdetect.lang_detect_exception import LangDetectException

class LanguageDetector:
    def __init__(self, fallback_lang='en'):
        self.fallback_lang = fallback_lang

    def detect(self, text: str) -> str:
        """
        Detects the language of the given text.
        Returns the ISO 639-1 language code (e.g., 'en', 'es').
        Falls back to self.fallback_lang if detection fails or text is too short/ambiguous.
        """
        if not text or not text.strip():
            return self.fallback_lang
            
        try:
            # langdetect works best with a bit of context. 
            # If the text is just a number or symbol, it might raise an exception.
            lang = langdetect.detect(text)
            return lang
        except LangDetectException:
            # Typically happens if there are no letters to detect language from
            return self.fallback_lang
