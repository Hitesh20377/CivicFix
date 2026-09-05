import logging
from typing import Optional
from ..extensions import db
from ..models.notifications import Notification
from ..models.enums import NotificationType
from ..models.user import User
from ..models.municipal import EmployeeProfile

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_notification(user_id: int, issue_id: int, notif_type: NotificationType, title: str, message: str, action_url: Optional[str] = None):
        """
        Creates an in-app notification.
        In a real scenario, this might also push to a WebSocket or queue an email.
        """
        notification = Notification(
            user_id=user_id,
            issue_id=issue_id,
            notification_type=notif_type,
            title=title,
            message=message,
            action_url=action_url
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def notify_citizen_issue_update(issue, notif_type: NotificationType, title: str, message: str):
        """Notify the citizen who reported the issue."""
        NotificationService.send_notification(
            user_id=issue.created_by,
            issue_id=issue.id,
            notif_type=notif_type,
            title=title,
            message=message,
            action_url=f"/issues/{issue.id}"
        )

    @staticmethod
    def notify_officers_in_ward(ward_id: int, issue, notif_type: NotificationType, title: str, message: str):
        """Notify all municipal officers in a specific ward."""
        officers = EmployeeProfile.query.join(User).filter(
            EmployeeProfile.ward_id == ward_id,
            User.role == UserRole.MUNICIPAL_OFFICER
        ).all()
        
        for officer in officers:
            NotificationService.send_notification(
                user_id=officer.user_id,
                issue_id=issue.id,
                notif_type=notif_type,
                title=title,
                message=message,
                action_url=f"/issues/manage/{issue.id}"
            )
