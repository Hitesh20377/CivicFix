from datetime import datetime
from ..extensions import db
from .enums import NotificationType

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=True)
    notification_type = db.Column(db.Enum(NotificationType), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    action_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))
    issue = db.relationship('Issue', backref=db.backref('notifications', lazy='dynamic'))

    __table_args__ = (
        db.Index('idx_user_is_read', 'user_id', 'is_read'),
    )

class NotificationPreference(db.Model):
    __tablename__ = 'notification_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    issue_submitted = db.Column(db.Boolean, default=True)
    issue_assigned = db.Column(db.Boolean, default=True)
    assignment_updated = db.Column(db.Boolean, default=True)
    status_changed = db.Column(db.Boolean, default=True)
    comment_added = db.Column(db.Boolean, default=True)
    sla_warning = db.Column(db.Boolean, default=True)
    sla_breached = db.Column(db.Boolean, default=True)
    issue_resolved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('notification_preferences', uselist=False))

