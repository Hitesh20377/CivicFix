from typing import Optional
from celery import shared_task
from app.services.notification_service import NotificationService
from app.models.enums import NotificationType
from .base_task import BaseTask

@shared_task(bind=True, base=BaseTask, name="tasks.send_notification")
def send_notification_task(self, user_id: int, issue_id: int, notif_type: str, title: str, message: str, action_url: Optional[str] = None):
    """
    Celery task to send a notification asynchronously.
    """
    try:
        # Convert string enum to actual enum type if needed, or pass directly
        enum_type = NotificationType[notif_type] if isinstance(notif_type, str) else notif_type
        
        NotificationService.send_notification(
            user_id=user_id,
            issue_id=issue_id,
            notif_type=enum_type,
            title=title,
            message=message,
            action_url=action_url
        )
        return {"status": "success", "user_id": user_id, "issue_id": issue_id}
    except Exception as e:
        self.retry(exc=e)


@shared_task(bind=True, base=BaseTask, name="tasks.process_issue_event")
def process_issue_event(self, issue_id: int, event_type: str, metadata: dict = None):
    """
    Process various issue events and trigger appropriate notifications based on rules.
    """
    try:
        from app.extensions import db
        from app.models.issue import Issue
        from app.models.enums import IssuePriority, UserRole
        from app.models.user import User
        from app.models.assignment import IssueAssignment
        from app.models.municipal import EmployeeProfile

        issue = Issue.query.get(issue_id)
        if not issue:
            return {"status": "error", "message": "Issue not found"}
            
        metadata = metadata or {}
        
        # Determine critical status
        is_critical = issue.official_priority == IssuePriority.CRITICAL
        
        # Helper to find officers
        def get_ward_officers():
            return [u for u, p in db.session.query(User, EmployeeProfile).join(EmployeeProfile, User.id == EmployeeProfile.user_id).filter(
                EmployeeProfile.ward_id == issue.ward_id,
                User.role == UserRole.MUNICIPAL_OFFICER
            ).all()]
            
        def get_admins():
            return User.query.filter_by(role=UserRole.ADMIN).all()
            
        def get_assigned_worker():
            assignment = IssueAssignment.query.filter_by(issue_id=issue.id).order_by(IssueAssignment.created_at.desc()).first()
            if assignment:
                return User.query.get(assignment.assigned_to)
            return None

        # Build recipients list based on event type and severity
        recipients = set()
        
        if is_critical and event_type in ['issue_submitted', 'sla_warning', 'sla_breached']:
            # Critical issues notify officers and admins immediately
            for officer in get_ward_officers():
                recipients.add(officer.id)
            for admin in get_admins():
                recipients.add(admin.id)
        else:
            # Normal flows
            if event_type in ['issue_submitted', 'issue_resolved', 'status_changed']:
                recipients.add(issue.created_by)
                for officer in get_ward_officers():
                    recipients.add(officer.id)
            
            if event_type == 'issue_assigned':
                assigned_to = metadata.get('assigned_to')
                if assigned_to:
                    recipients.add(assigned_to)
                    
            if event_type in ['sla_warning', 'sla_breached']:
                for officer in get_ward_officers():
                    recipients.add(officer.id)
                worker = get_assigned_worker()
                if worker:
                    recipients.add(worker.id)
                    
        # Send notifications
        title = f"Issue {issue.issue_number} Update"
        if event_type == 'issue_submitted':
            message = "A new issue has been submitted."
            mapped_notif_type = NotificationType.ISSUE_SUBMITTED
        elif event_type == 'sla_warning':
            message = "Warning: Issue SLA is approaching breach."
            mapped_notif_type = NotificationType.SLA_APPROACHING
        elif event_type == 'sla_breached':
            message = "Alert: Issue SLA has breached!"
            mapped_notif_type = NotificationType.SLA_BREACHED
        elif event_type == 'issue_resolved':
            message = "Issue has been resolved."
            mapped_notif_type = NotificationType.ISSUE_RESOLVED
        else:
            message = f"Issue status or details have been updated."
            mapped_notif_type = NotificationType.ISSUE_MOVED_REVIEW

        for user_id in recipients:
            NotificationService.send_notification(
                user_id=user_id,
                issue_id=issue.id,
                notif_type=mapped_notif_type,
                title=title,
                message=message,
                action_url=f"/issues/{issue.id}"
            )
            
        return {"status": "success", "notified_count": len(recipients)}
    except Exception as e:
        self.retry(exc=e)
