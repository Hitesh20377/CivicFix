from datetime import datetime
from ..extensions import db
from .enums import AssignmentStatus

class IssueAssignment(db.Model):
    __tablename__ = 'issue_assignments'

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    ward_id = db.Column(db.Integer, db.ForeignKey('wards.id'), nullable=True)
    assignment_status = db.Column(db.Enum(AssignmentStatus), nullable=False, default=AssignmentStatus.ASSIGNED)
    assignment_note = db.Column(db.Text, nullable=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    issue = db.relationship('Issue', backref=db.backref('assignments', lazy='dynamic'))
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref=db.backref('tasks_assigned_to_me', lazy='dynamic'))
    assigner = db.relationship('User', foreign_keys=[assigned_by], backref=db.backref('tasks_assigned_by_me', lazy='dynamic'))

    __table_args__ = (
        db.Index('idx_issue_assignment_status', 'issue_id', 'assignment_status'),
    )

class AssignmentHistory(db.Model):
    __tablename__ = 'assignment_history'

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    previous_assignee = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    new_assignee = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    issue = db.relationship('Issue', backref=db.backref('assignment_history', lazy='dynamic'))
    prev_user = db.relationship('User', foreign_keys=[previous_assignee])
    new_user = db.relationship('User', foreign_keys=[new_assignee])
    changer = db.relationship('User', foreign_keys=[changed_by])
