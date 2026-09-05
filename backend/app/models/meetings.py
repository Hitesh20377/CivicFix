from datetime import datetime
import enum
from ..extensions import db

class ActionItemStatus(str, enum.Enum):
    NEEDS_REVIEW = "needs_review"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class Meeting(db.Model):
    """
    Meeting model representing a scheduled or recorded meeting.
    Tracks calendar integration and human-approval status for note sharing.
    """
    __tablename__ = 'meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    
    calendar_event_id = db.Column(db.String(255), nullable=True)
    calendar_provider = db.Column(db.String(50), nullable=True) # e.g. 'google', 'microsoft'
    
    # Crucial constraint: human approval
    summary_approved_at = db.Column(db.DateTime, nullable=True)
    approved_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_summary_shared = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_meetings_calendar_event_id', 'calendar_event_id'),
    )

class ActionItem(db.Model):
    """
    ActionItem model for tracking tasks extracted from meeting transcripts.
    """
    __tablename__ = 'action_items'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, nullable=False) # Stub link to meeting
    
    task_text = db.Column(db.Text, nullable=False)
    normalized_task_text = db.Column(db.Text, nullable=False)
    
    owner_name = db.Column(db.String(255), nullable=True)
    owner_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    deadline = db.Column(db.DateTime, nullable=True)
    deadline_text = db.Column(db.String(255), nullable=True)
    
    priority = db.Column(db.String(50), nullable=True) # e.g. low, medium, high
    status = db.Column(db.Enum(ActionItemStatus), nullable=False, default=ActionItemStatus.NEEDS_REVIEW)
    confidence_score = db.Column(db.Float, nullable=True)
    
    source_start_seconds = db.Column(db.Float, nullable=True)
    source_end_seconds = db.Column(db.Float, nullable=True)
    source_segment_id = db.Column(db.Integer, nullable=True)
    
    extraction_method = db.Column(db.String(100), nullable=True)
    model_name = db.Column(db.String(100), nullable=True)
    model_version = db.Column(db.String(50), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.Index('idx_action_items_meeting_id', 'meeting_id'),
        db.Index('idx_action_items_status', 'status'),
        db.Index('idx_action_items_owner', 'owner_user_id'),
    )
