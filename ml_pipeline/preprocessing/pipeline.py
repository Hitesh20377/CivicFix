from typing import List, Dict, Any
from .cleaner import TextCleaner
from .segment_processor import SegmentProcessor
from .language_detector import LanguageDetector
from .text_statistics import TextStatistics

class TranscriptPreprocessor:
    def __init__(self, remove_stuttering=True, remove_stop_words=False, fallback_lang='en'):
        self.cleaner = TextCleaner(remove_stuttering=remove_stuttering, remove_stop_words=remove_stop_words)
        self.segment_processor = SegmentProcessor()
        self.language_detector = LanguageDetector(fallback_lang=fallback_lang)
        self.statistics = TextStatistics()

    def process(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes a list of raw transcript segments through the entire pipeline.
        Returns a list of cleaned and enriched segments.
        """
        processed_segments = []
        
        for raw_segment in segments:
            # 1. Structural validation and metadata preservation
            segment = self.segment_processor.process(raw_segment)
            if not segment:
                continue
                
            # 2. Text cleaning (unicode, whitespace, optional stutter/stopword removal)
            original_text = segment['text']
            cleaned_text = self.cleaner.clean(original_text)
            
            if not cleaned_text:
                continue
                
            # 3. Calculate text statistics on the cleaned text
            stats = self.statistics.calculate(cleaned_text)
            
            # 4. Language detection
            lang = self.language_detector.detect(cleaned_text)
            
            # Combine into final enriched segment
            enriched_segment = {
                **segment,
                'original_text': original_text,
                'text': cleaned_text,  # replace with cleaned version for ML
                'word_count': stats['word_count'],
                'sentence_count': stats['sentence_count'],
                'language': lang
            }
            
            processed_segments.append(enriched_segment)
            
        return processed_segments
