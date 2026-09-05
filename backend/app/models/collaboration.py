from datetime import datetime
from ..extensions import db
from .enums import ParticipantRole, ParticipationStatus, TargetEntityType

class MeetingParticipant(db.Model):
    """
    Model for tracking who is involved in a meeting and their roles.
    """
    __tablename__ = 'meeting_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    display_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    
    role = db.Column(db.Enum(ParticipantRole), nullable=False, default=ParticipantRole.PARTICIPANT)
    participation_status = db.Column(db.Enum(ParticipationStatus), nullable=False, default=ParticipationStatus.INVITED)
    
    invited_at = db.Column(db.DateTime, default=datetime.utcnow)
    joined_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_participant_meeting', 'meeting_id'),
        db.Index('idx_participant_user', 'user_id'),
    )

class MeetingComment(db.Model):
    """
    Model for users to leave comments or suggest corrections on AI-generated content.
    """
    __tablename__ = 'meeting_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'), nullable=False)
    author_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    target_entity_type = db.Column(db.Enum(TargetEntityType), nullable=False)
    target_entity_id = db.Column(db.Integer, nullable=False) # ID of the action item, segment, etc.
    
    content = db.Column(db.Text, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentVersion(db.Model):
    """
    Audit log / Version Control table to track edits, corrections, and restorations
    across all AI-generated entities (Action Items, Decisions, Summaries, etc.)
    """
    __tablename__ = 'content_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'), nullable=False)
    
    target_entity_type = db.Column(db.Enum(TargetEntityType), nullable=False)
    target_entity_id = db.Column(db.Integer, nullable=False)
    
    edited_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Store the state before and after the edit. Using JSON to handle varying schemas.
    previous_content = db.Column(db.JSON, nullable=False)
    new_content = db.Column(db.JSON, nullable=False)
    
    edit_reason = db.Column(db.String(500), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_version_entity', 'target_entity_type', 'target_entity_id'),
    )

class MeetingApprovalRecord(db.Model):
    """
    Tracks the granular approval lifecycle by reviewers before sharing is permitted.
    """
    __tablename__ = 'meeting_approval_records'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'), nullable=False)
    reviewer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    status = db.Column(db.String(50), nullable=False) # 'approved', 'rejected', 'pending'
    feedback_notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
