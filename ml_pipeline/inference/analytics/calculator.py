from typing import List, Dict, Any

class MeetingMetricsCalculator:
    """
    Calculates operational and effectiveness metrics for a meeting.
    Does not evaluate individual employee performance.
    """
    def __init__(self):
        self.version = "1.0"
        
    def calculate_metrics(self, meeting_id: int, segments: List[Dict[str, Any]], 
                          action_items: List[Dict[str, Any]], 
                          decisions: List[Dict[str, Any]], 
                          unresolved_questions: List[Dict[str, Any]], 
                          risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Takes raw data and generates a structured metrics dictionary.
        """
        # Duration and Word Counts
        duration = 0.0
        total_words = 0
        speakers = set()
        
        if segments:
            # Assumes segments are ordered by time
            duration = segments[-1].get("end_time", 0.0) - segments[0].get("start_time", 0.0)
            
        for segment in segments:
            speakers.add(segment.get("speaker"))
            total_words += len(segment.get("text", "").split())
            
        wpm = (total_words / (duration / 60)) if duration > 0 else 0.0
        
        # Action Item Rates
        action_item_count = len(action_items)
        items_with_owners = sum(1 for item in action_items if item.get("owner_name"))
        items_with_deadlines = sum(1 for item in action_items if item.get("deadline_text"))
        completed_items = sum(1 for item in action_items if item.get("status") == "completed")
        
        owner_rate = (items_with_owners / action_item_count) if action_item_count > 0 else 1.0
        deadline_rate = (items_with_deadlines / action_item_count) if action_item_count > 0 else 1.0
        completion_rate = (completed_items / action_item_count) if action_item_count > 0 else 0.0
        
        # Effectiveness Score Components
        decision_clarity = 1.0 if len(decisions) > 0 else 0.5
        action_completeness = (owner_rate + deadline_rate) / 2.0
        topic_focus = 0.8 # Placeholder for topic clustering focus
        
        question_count = len(unresolved_questions)
        question_resolution = max(0.0, 1.0 - (question_count * 0.1)) # Deduct for many unresolved questions
        
        follow_up_quality = action_completeness
        
        # Formula
        effectiveness_score = (
            (0.25 * decision_clarity) +
            (0.25 * action_completeness) +
            (0.20 * topic_focus) +
            (0.15 * question_resolution) +
            (0.15 * follow_up_quality)
        )
        
        return {
            "meeting_id": meeting_id,
            "duration_seconds": duration,
            "speaker_count": len(speakers),
            "total_word_count": total_words,
            "words_per_minute": wpm,
            "decision_count": len(decisions),
            "action_item_count": action_item_count,
            "unresolved_question_count": question_count,
            "risk_count": len(risks),
            "owner_assignment_rate": owner_rate,
            "deadline_assignment_rate": deadline_rate,
            "action_completion_rate": completion_rate,
            "meeting_effectiveness_score": round(effectiveness_score, 2),
            "analytics_version": self.version
        }
