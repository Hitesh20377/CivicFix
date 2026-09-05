from datetime import datetime
from ..extensions import db
from .enums import IssuePriority

class SLAPolicy(db.Model):
    __tablename__ = 'sla_policies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('issue_categories.id'), nullable=True)
    priority = db.Column(db.Enum(IssuePriority), nullable=False)
    response_time_minutes = db.Column(db.Integer, nullable=False)
    resolution_time_minutes = db.Column(db.Integer, nullable=False)
    escalation_time_minutes = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IssueSLA(db.Model):
    __tablename__ = 'issue_slas'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    sla_policy_id = db.Column(db.Integer, db.ForeignKey('sla_policies.id'), nullable=False)
    response_due_at = db.Column(db.DateTime, nullable=False)
    resolution_due_at = db.Column(db.DateTime, nullable=False)
    responded_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    response_breached = db.Column(db.Boolean, default=False)
    resolution_breached = db.Column(db.Boolean, default=False)
    warning_sent = db.Column(db.Boolean, default=False)
    breach_notification_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    issue = db.relationship('Issue', backref=db.backref('sla', uselist=False))
    policy = db.relationship('SLAPolicy')

class EscalationRecord(db.Model):
    __tablename__ = 'escalation_records'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    escalation_level = db.Column(db.Integer, nullable=False, default=1)
    escalated_from = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    escalated_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    escalated_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    issue = db.relationship('Issue', backref=db.backref('escalations', lazy='dynamic'))
    from_user = db.relationship('User', foreign_keys=[escalated_from])
    to_user = db.relationship('User', foreign_keys=[escalated_to])
