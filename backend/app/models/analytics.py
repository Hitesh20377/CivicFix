from datetime import datetime
from ..extensions import db

class MeetingAnalytics(db.Model):
    """
    Model for tracking meeting effectiveness and operational analytics.
    Does not track individual employee performance.
    """
    __tablename__ = 'meeting_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, nullable=False, unique=True)
    
    # Base metrics
    duration_seconds = db.Column(db.Float, default=0.0)
    participant_count = db.Column(db.Integer, default=0)
    speaker_count = db.Column(db.Integer, default=0)
    total_word_count = db.Column(db.Integer, default=0)
    words_per_minute = db.Column(db.Float, default=0.0)
    
    # Pipeline Extraction counts
    topic_count = db.Column(db.Integer, default=0)
    topic_switch_count = db.Column(db.Integer, default=0)
    decision_count = db.Column(db.Integer, default=0)
    action_item_count = db.Column(db.Integer, default=0)
    unresolved_question_count = db.Column(db.Integer, default=0)
    risk_count = db.Column(db.Integer, default=0)
    
    # Ratios and Rates
    average_transcript_confidence = db.Column(db.Float, default=0.0)
    owner_assignment_rate = db.Column(db.Float, default=0.0)
    deadline_assignment_rate = db.Column(db.Float, default=0.0)
    action_completion_rate = db.Column(db.Float, default=0.0)
    
    # Effectiveness Score
    meeting_effectiveness_score = db.Column(db.Float, default=0.0)
    
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    analytics_version = db.Column(db.String(50), nullable=True)

    __table_args__ = (
        db.Index('idx_meeting_analytics_meeting_id', 'meeting_id'),
    )
