class SegmentProcessor:
    def __init__(self):
        # We can add configurable rules here later, e.g. min_length
        self.required_keys = ['meeting_id', 'segment_id', 'text']
        
    def process(self, segment: dict) -> dict:
        """
        Validates and processes a single segment dictionary.
        Returns the processed segment or None if invalid.
        """
        if not isinstance(segment, dict):
            return None
            
        # Check for required keys
        for key in self.required_keys:
            if key not in segment:
                return None
                
        # Must have actual text content
        if not segment.get('text') or not str(segment['text']).strip():
            return None
            
        processed = {
            'meeting_id': segment['meeting_id'],
            'segment_id': segment['segment_id'],
            'text': str(segment['text']),
            'speaker': segment.get('speaker', 'Unknown Speaker')
        }
        
        # Validate timestamps if present
        start = segment.get('start_time')
        end = segment.get('end_time')
        
        if start is not None and end is not None:
            try:
                start_f = float(start)
                end_f = float(end)
                if start_f >= 0 and end_f >= start_f:
                    processed['start_time'] = start_f
                    processed['end_time'] = end_f
                else:
                    # Invalid timestamps, set to None
                    processed['start_time'] = None
                    processed['end_time'] = None
            except (ValueError, TypeError):
                processed['start_time'] = None
                processed['end_time'] = None
        else:
            processed['start_time'] = None
            processed['end_time'] = None
            
        return processed
