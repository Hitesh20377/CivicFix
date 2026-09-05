import pytest
from unittest.mock import patch, MagicMock
from app.tasks.notification_tasks import send_notification_task, process_issue_event
from app.models.enums import NotificationType, IssuePriority, UserRole
from app.models.user import User
from app.models.municipal import EmployeeProfile, Ward, Department
from app.models.issue import Issue, IssueCategory
from app.models.assignment import IssueAssignment
from app.models.enums import AssignmentStatus
from app.extensions import db

def test_send_notification_task(app):
    with patch('app.services.notification_service.NotificationService.send_notification') as mock_send:
        result = send_notification_task(
            user_id=1,
            issue_id=1,
            notif_type='ISSUE_SUBMITTED',
            title='Test',
            message='Test Message',
            action_url=None
        )
        assert result['status'] == 'success'
        mock_send.assert_called_once_with(
            user_id=1,
            issue_id=1,
            notif_type=NotificationType.ISSUE_SUBMITTED,
            title='Test',
            message='Test Message',
            action_url=None
        )


def test_process_issue_event_normal(app):
    # Setup data is already present in app fixture from conftest.py
    ward = Ward.query.first()
    officer = User.query.filter_by(role=UserRole.MUNICIPAL_OFFICER).first()
    worker_profile = EmployeeProfile.query.first()
    
    # ensure officer has a profile linking to the ward
    profile = EmployeeProfile(user_id=officer.id, department_id=worker_profile.department_id, ward_id=ward.id, employee_code="EMP-OFFICER", designation="Officer")
    db.session.add(profile)
    
    citizen = User(email='citizen_test@example.com', full_name='Citizen Test', role=UserRole.CITIZEN, is_active=True, password_hash='dummy')
    db.session.add(citizen)
    db.session.commit()
    
    issue = Issue.query.first()
    issue.created_by = citizen.id
    db.session.commit()
    
    # Test issue_submitted event
    with patch('app.services.notification_service.NotificationService.send_notification') as mock_send:
        result = process_issue_event(
            issue_id=issue.id,
            event_type='issue_submitted',
            metadata=None
        )
        assert result['status'] == 'success'
        # Created_by and Ward Officer should receive it
        assert mock_send.call_count == 2
        notified_users = [call[1]['user_id'] for call in mock_send.call_args_list]
        assert issue.created_by in notified_users
        assert officer.id in notified_users

def test_process_issue_event_critical(app):
    issue = Issue.query.first()
    issue.official_priority = IssuePriority.CRITICAL
    db.session.commit()
    
    ward = Ward.query.first()
    officer = User.query.filter_by(role=UserRole.MUNICIPAL_OFFICER).first()
    worker_profile = EmployeeProfile.query.first()
    
    # ensure officer has a profile linking to the ward
    if not EmployeeProfile.query.filter_by(user_id=officer.id).first():
        profile = EmployeeProfile(user_id=officer.id, department_id=worker_profile.department_id, ward_id=ward.id, employee_code="EMP-OFFICER2", designation="Officer")
        db.session.add(profile)
        db.session.commit()
    
    # Add an admin
    admin = User(email='admin_crit@example.com', full_name='Admin', role=UserRole.ADMIN, is_active=True, password_hash='dummy')
    db.session.add(admin)
    db.session.commit()
    
    with patch('app.services.notification_service.NotificationService.send_notification') as mock_send:
        result = process_issue_event(
            issue_id=issue.id,
            event_type='sla_warning',
            metadata=None
        )
        assert result['status'] == 'success'
        # Officer and Admin should receive it
        assert mock_send.call_count == 2
        notified_users = [call[1]['user_id'] for call in mock_send.call_args_list]
        assert officer.id in notified_users
        assert admin.id in notified_users
