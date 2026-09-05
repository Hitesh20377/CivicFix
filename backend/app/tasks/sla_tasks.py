from celery import shared_task
from datetime import datetime
from app.extensions import db
from app.models.sla import IssueSLA, SLAPolicy
from app.models.issue import Issue
from app.services.sla_service import SLAService
from app.tasks.notification_tasks import process_issue_event
from .base_task import BaseTask
import structlog

logger = structlog.get_logger()

@shared_task(bind=True, base=BaseTask, name="tasks.check_sla_breaches")
def check_sla_breaches_task(self):
    """
    Periodic task to check for SLA breaches and update records.
    """
    try:
        now = datetime.utcnow()
        breached_slas = []
        
        # Check SLA warnings (80%)
        # Unresponded issues
        unresponded_slas = IssueSLA.query.filter(
            IssueSLA.responded_at.is_(None),
            IssueSLA.warning_sent == False,
            IssueSLA.response_breached == False
        ).all()
        for sla in unresponded_slas:
            total_time = (sla.response_due_at - sla.created_at).total_seconds()
            elapsed = (now - sla.created_at).total_seconds()
            if total_time > 0 and elapsed >= 0.8 * total_time:
                sla.warning_sent = True
                logger.info("SLA response warning", issue_id=sla.issue_id)
                process_issue_event.delay(sla.issue_id, 'sla_warning', metadata={'type': 'response'})

        # Unresolved issues
        unresolved_slas_warning = IssueSLA.query.filter(
            IssueSLA.resolved_at.is_(None),
            IssueSLA.warning_sent == False,
            IssueSLA.resolution_breached == False
        ).all()
        for sla in unresolved_slas_warning:
            total_time = (sla.resolution_due_at - sla.created_at).total_seconds()
            elapsed = (now - sla.created_at).total_seconds()
            if total_time > 0 and elapsed >= 0.8 * total_time:
                sla.warning_sent = True
                logger.info("SLA resolution warning", issue_id=sla.issue_id)
                process_issue_event.delay(sla.issue_id, 'sla_warning', metadata={'type': 'resolution'})

        # Check response breaches
        unresponded_slas_breach = IssueSLA.query.filter(
            IssueSLA.responded_at.is_(None),
            IssueSLA.response_due_at < now,
            IssueSLA.response_breached == False
        ).all()
        
        for sla in unresponded_slas_breach:
            sla.response_breached = True
            breached_slas.append(sla.issue_id)
            logger.info("SLA response breached", issue_id=sla.issue_id)
            process_issue_event.delay(sla.issue_id, 'sla_breached', metadata={'type': 'response'})

        # Check resolution breaches
        unresolved_slas_breach = IssueSLA.query.filter(
            IssueSLA.resolved_at.is_(None),
            IssueSLA.resolution_due_at < now,
            IssueSLA.resolution_breached == False
        ).all()
        
        for sla in unresolved_slas_breach:
            sla.resolution_breached = True
            breached_slas.append(sla.issue_id)
            logger.info("SLA resolution breached", issue_id=sla.issue_id)
            process_issue_event.delay(sla.issue_id, 'sla_breached', metadata={'type': 'resolution'})

        if breached_slas or unresponded_slas or unresolved_slas_warning:
            db.session.commit()
            
        return {"status": "success", "breached_issues": list(set(breached_slas))}
    except Exception as e:
        db.session.rollback()
        self.retry(exc=e)

@shared_task(bind=True, base=BaseTask, name="tasks.auto_escalate_issue")
def auto_escalate_issue_task(self, issue_id: int, escalated_from_id: int, escalated_to_id: int, reason: str, level: int = 1):
    """
    Asynchronously auto-escalate an issue.
    """
    try:
        SLAService.escalate_issue(
            issue_id=issue_id,
            escalated_from_id=escalated_from_id,
            escalated_to_id=escalated_to_id,
            reason=reason,
            level=level
        )
        return {"status": "success", "issue_id": issue_id, "escalated_to": escalated_to_id}
    except Exception as e:
        self.retry(exc=e)

@shared_task(bind=True, base=BaseTask, name="tasks.calculate_issue_sla")
def calculate_issue_sla(self, issue_id: int):
    """
    Calculate and apply the SLA for an issue asynchronously.
    """
    try:
        issue = Issue.query.get(issue_id)
        if not issue:
            return {"status": "error", "message": "Issue not found"}
            
        # Try to find a matching policy for category and priority
        policy = SLAPolicy.query.filter_by(
            category_id=issue.category_id,
            priority=issue.official_priority,
            is_active=True
        ).first()
        
        # If no policy for category, try default category (None) with same priority
        if not policy:
            policy = SLAPolicy.query.filter_by(
                category_id=None,
                priority=issue.official_priority,
                is_active=True
            ).first()
            
        if policy:
            SLAService.apply_sla_to_issue(issue_id, policy.id)
            return {"status": "success", "issue_id": issue_id, "policy_id": policy.id}
        else:
            return {"status": "error", "message": "No SLA policy found for issue"}
    except Exception as e:
        self.retry(exc=e)
