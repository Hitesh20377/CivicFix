import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from app.tasks.sla_tasks import check_sla_breaches_task, calculate_issue_sla
from app.models.sla import IssueSLA, SLAPolicy
from app.models.issue import Issue
from app.models.enums import IssuePriority
from app.extensions import db

def test_calculate_issue_sla(app):
    issue = Issue.query.first()
    if not issue.official_priority:
        issue.official_priority = IssuePriority.MEDIUM
        db.session.commit()
        
    # Create a matching SLA policy
    policy = SLAPolicy(
        name="Test Policy",
        category_id=issue.category_id,
        priority=issue.official_priority,
        response_time_minutes=120,
        resolution_time_minutes=1440,
        escalation_time_minutes=60,
        is_active=True
    )
    db.session.add(policy)
    db.session.commit()
    
    with patch('app.services.sla_service.SLAService.apply_sla_to_issue') as mock_apply:
        result = calculate_issue_sla(issue_id=issue.id)
        assert result['status'] == 'success'
        assert result['policy_id'] == policy.id
        mock_apply.assert_called_once_with(issue.id, policy.id)

def test_check_sla_breaches_task(app):
    issue = Issue.query.first()
    if not issue.official_priority:
        issue.official_priority = IssuePriority.MEDIUM
        db.session.commit()
        
    policy = SLAPolicy.query.first()
    if not policy:
        policy = SLAPolicy(
            name="Test Policy 2",
            category_id=issue.category_id,
            priority=issue.official_priority,
            response_time_minutes=120,
            resolution_time_minutes=1440,
            escalation_time_minutes=60,
            is_active=True
        )
        db.session.add(policy)
        db.session.commit()
        
    now = datetime.utcnow()
    
    # Create an SLA that is approaching breach (80% of time elapsed)
    created_at = now - timedelta(hours=2)
    response_due = created_at + timedelta(hours=2.5) # total 2.5h, elapsed 2h = 80%
    resolution_due = created_at + timedelta(hours=24)
    
    sla = IssueSLA(
        issue_id=issue.id,
        sla_policy_id=policy.id,
        created_at=created_at,
        response_due_at=response_due,
        resolution_due_at=resolution_due
    )
    db.session.add(sla)
    db.session.commit()
    
    with patch('app.tasks.sla_tasks.process_issue_event.delay') as mock_process:
        result = check_sla_breaches_task()
        assert result['status'] == 'success'
        
        # The SLA response warning should be triggered
        mock_process.assert_any_call(issue.id, 'sla_warning', metadata={'type': 'response'})
        
        # Verify the DB was updated
        updated_sla = IssueSLA.query.filter_by(issue_id=issue.id).order_by(IssueSLA.id.desc()).first()
        assert updated_sla.warning_sent == True
        assert updated_sla.response_breached == False

def test_check_sla_breaches_breach(app):
    issue = Issue.query.first()
    if not issue.official_priority:
        issue.official_priority = IssuePriority.MEDIUM
        db.session.commit()
        
    policy = SLAPolicy.query.first()
    if not policy:
        policy = SLAPolicy(
            name="Test Policy 3",
            category_id=issue.category_id,
            priority=issue.official_priority,
            response_time_minutes=120,
            resolution_time_minutes=1440,
            escalation_time_minutes=60,
            is_active=True
        )
        db.session.add(policy)
        db.session.commit()
    
    now = datetime.utcnow()
    
    # Create an SLA that is already breached
    created_at = now - timedelta(hours=3)
    response_due = created_at + timedelta(hours=2) # Past due
    resolution_due = created_at + timedelta(hours=24)
    
    sla = IssueSLA(
        issue_id=issue.id,
        sla_policy_id=policy.id,
        created_at=created_at,
        response_due_at=response_due,
        resolution_due_at=resolution_due
    )
    db.session.add(sla)
    db.session.commit()
    
    with patch('app.tasks.sla_tasks.process_issue_event.delay') as mock_process:
        result = check_sla_breaches_task()
        assert result['status'] == 'success'
        assert issue.id in result['breached_issues']
        
        # The SLA breached should be triggered
        mock_process.assert_any_call(issue.id, 'sla_breached', metadata={'type': 'response'})
        
        updated_sla = IssueSLA.query.filter_by(issue_id=issue.id).order_by(IssueSLA.id.desc()).first()
        assert updated_sla.response_breached == True
