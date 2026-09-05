from typing import Optional
from datetime import datetime, timedelta
from ..extensions import db
from ..models.sla import IssueSLA, SLAPolicy, EscalationRecord
from ..models.issue import Issue
from ..models.user import User
from ..models.enums import UserRole

class SLAService:
    @staticmethod
    def calculate_due_dates(issue: Issue, policy: SLAPolicy):
        """Calculate due dates for response and resolution based on policy."""
        now = datetime.utcnow()
        response_due = now + timedelta(minutes=policy.response_time_minutes)
        resolution_due = now + timedelta(minutes=policy.resolution_time_minutes)
        return response_due, resolution_due

    @staticmethod
    def apply_sla_to_issue(issue_id: int, policy_id: int) -> IssueSLA:
        """Apply an SLA policy to a newly created issue."""
        issue = Issue.query.get(issue_id)
        policy = SLAPolicy.query.get(policy_id)
        
        if not issue or not policy:
            raise ValueError("Invalid issue or policy ID")
            
        response_due, resolution_due = SLAService.calculate_due_dates(issue, policy)
        
        sla = IssueSLA(
            issue_id=issue_id,
            sla_policy_id=policy_id,
            response_due_at=response_due,
            resolution_due_at=resolution_due
        )
        db.session.add(sla)
        db.session.commit()
        return sla

    @staticmethod
    def record_response(issue_id: int) -> Optional[IssueSLA]:
        """Mark the issue as responded to, recording the time and checking for breach."""
        sla = IssueSLA.query.filter_by(issue_id=issue_id).first()
        if not sla:
            return None
            
        if not sla.responded_at:
            sla.responded_at = datetime.utcnow()
            if sla.responded_at > sla.response_due_at:
                sla.response_breached = True
            db.session.commit()
        return sla

    @staticmethod
    def record_resolution(issue_id: int) -> Optional[IssueSLA]:
        """Mark the issue as resolved, checking for resolution breach."""
        sla = IssueSLA.query.filter_by(issue_id=issue_id).first()
        if not sla:
            return None
            
        if not sla.resolved_at:
            sla.resolved_at = datetime.utcnow()
            if sla.resolved_at > sla.resolution_due_at:
                sla.resolution_breached = True
            db.session.commit()
        return sla

    @staticmethod
    def escalate_issue(issue_id: int, escalated_from_id: int, escalated_to_id: int, reason: str, level: int = 1) -> EscalationRecord:
        """Escalate an issue to a higher level of authority."""
        escalation = EscalationRecord(
            issue_id=issue_id,
            escalated_from=escalated_from_id,
            escalated_to=escalated_to_id,
            reason=reason,
            escalation_level=level
        )
        db.session.add(escalation)
        db.session.commit()
        
        # Here we would also typically trigger a notification via NotificationService
        return escalation
