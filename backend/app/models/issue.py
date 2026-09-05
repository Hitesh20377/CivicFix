from datetime import datetime
from ..extensions import db
from .enums import IssueStatus, IssuePriority

class IssueCategory(db.Model):
    """IssueCategory model."""
    __tablename__ = 'issue_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Issue(db.Model):
    """Real Issue model."""
    __tablename__ = 'issues'

    id = db.Column(db.Integer, primary_key=True)
    issue_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    category_id = db.Column(db.Integer, db.ForeignKey('issue_categories.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ward_id = db.Column(db.Integer, db.ForeignKey('wards.id'), nullable=True)
    
    address = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    citizen_priority = db.Column(db.Enum(IssuePriority), nullable=False, default=IssuePriority.LOW)
    official_priority = db.Column(db.Enum(IssuePriority), nullable=True)
    status = db.Column(db.Enum(IssueStatus), nullable=False, default=IssueStatus.SUBMITTED)
    
    # ML Tracking Fields from stub
    suggested_category = db.Column(db.String(100), nullable=True)
    category_confidence = db.Column(db.Float, nullable=True)
    suggested_priority = db.Column(db.String(50), nullable=True)
    priority_reason = db.Column(db.Text, nullable=True)
    priority_confidence = db.Column(db.Float, nullable=True)
    model_version = db.Column(db.String(50), nullable=True)
    is_prediction_accepted = db.Column(db.Boolean, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)

    attachments = db.relationship('IssueAttachment', backref='issue', lazy=True, cascade='all, delete-orphan')
    status_history = db.relationship('IssueStatusHistory', backref='issue', lazy=True, cascade='all, delete-orphan')

    __table_args__ = (
        db.Index('idx_issue_status', 'status'),
        db.Index('idx_issue_ward_id', 'ward_id'),
        db.Index('idx_issue_created_at', 'created_at'),
    )

class IssueAttachment(db.Model):
    """IssueAttachment model."""
    __tablename__ = 'issue_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    storage_key = db.Column(db.String(255), nullable=False, unique=True)
    file_type = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, nullable=True) # size in bytes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class IssueStatusHistory(db.Model):
    """IssueStatusHistory model."""
    __tablename__ = 'issue_status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    old_status = db.Column(db.Enum(IssueStatus), nullable=True)
    new_status = db.Column(db.Enum(IssueStatus), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
