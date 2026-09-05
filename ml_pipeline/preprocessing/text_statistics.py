import re
import nltk

class TextStatistics:
    def __init__(self):
        # Ensure the punkt tokenizer model is available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

    def calculate(self, text: str) -> dict:
        """
        Calculates basic text statistics like word count and sentence count.
        """
        if not text or not str(text).strip():
            return {
                "word_count": 0,
                "sentence_count": 0
            }
            
        # Word count: splitting by whitespace and removing empty tokens
        # We can also use a simple regex to find words to avoid counting punctuation as words
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        # Sentence count: using NLTK's sentence tokenizer
        sentences = nltk.sent_tokenize(text)
        sentence_count = len(sentences)
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count
        }
