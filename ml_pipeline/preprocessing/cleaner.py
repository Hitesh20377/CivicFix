import re
import unicodedata

class TextCleaner:
    def __init__(self, remove_stuttering=True, remove_stop_words=False):
        self.remove_stuttering = remove_stuttering
        self.remove_stop_words = remove_stop_words
        self.stop_words = set()
        
        if self.remove_stop_words:
            try:
                import nltk
                from nltk.corpus import stopwords
                # Download stopwords if not available
                try:
                    self.stop_words = set(stopwords.words('english'))
                except LookupError:
                    nltk.download('stopwords', quiet=True)
                    self.stop_words = set(stopwords.words('english'))
            except ImportError:
                # Fallback to a basic list if nltk is not installed
                self.stop_words = {"a", "an", "the", "and", "but", "if", "or", "because", "as", "what", "which", "this", "that"}

    def clean(self, text: str) -> str:
        if not text:
            return ""

        # Normalize unicode (NFC/NFKC)
        text = unicodedata.normalize('NFKC', text)
        
        # Remove extra whitespace (tabs, newlines, multiple spaces)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove stuttering / repeated words (e.g. "I I think" -> "I think")
        # Matches word boundaries and backreferences
        if self.remove_stuttering:
            # Case insensitive match for consecutive identical words
            text = re.sub(r'\b(\w+)(?:\s+\1\b)+', r'\1', text, flags=re.IGNORECASE)

        # Remove stop words if configured
        if self.remove_stop_words and self.stop_words:
            words = text.split()
            words = [w for w in words if w.lower() not in self.stop_words]
            text = " ".join(words)

        return text
