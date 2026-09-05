import pytest
from app.models.user import User
from app.models.enums import UserRole, AssignmentStatus
from app.models.municipal import Ward, Department, EmployeeProfile
from app.models.issue import Issue, IssueCategory
from app.models.assignment import IssueAssignment
from app.extensions import db

def test_get_eligible_workers(client, auth_headers):
    # This requires setting up an Admin/Officer, some wards, depts, and workers
    headers = auth_headers('officer1@example.com')
    
    # In test DB, find an issue or create one
    issue = Issue.query.first()
    
    response = client.get(f'/api/assignments/eligible-workers/{issue.id}', headers=headers)
    assert response.status_code == 200
    workers = response.json
    assert isinstance(workers, list)
    
def test_create_assignment_invalid_worker(client, auth_headers):
    # Assign to someone unavailable or wrong ward
    headers = auth_headers('officer1@example.com')
    
    # Create an unassigned issue for this test
    ward = Ward.query.first()
    issue = Issue(
        title="Unassigned Issue",
        description="Test",
        issue_number="TEST-999",
        created_by=User.query.first().id,
        ward_id=ward.id
    )
    db.session.add(issue)
    db.session.commit()
    citizen_worker = User.query.filter_by(role=UserRole.CITIZEN).first()
    
    if citizen_worker:
        data = {
            'issue_id': issue.id,
            'assigned_to': citizen_worker.id
        }
        response = client.post('/api/assignments', json=data, headers=headers)
        assert response.status_code == 404
        assert "Worker not found" in response.json['error']

def test_prevent_duplicate_assignment(client, auth_headers):
    headers = auth_headers('officer1@example.com')
    
    # Find an issue already assigned
    assignment = IssueAssignment.query.filter_by(assignment_status=AssignmentStatus.ASSIGNED).first()
    if assignment:
        data = {
            'issue_id': assignment.issue_id,
            'assigned_to': assignment.assigned_to
        }
        response = client.post('/api/assignments', json=data, headers=headers)
        assert response.status_code == 400
        assert "already has an active assignment" in response.json['error']

def test_transition_status_reject_requires_reason(client, auth_headers):
    # Need a field worker to reject
    assignment = IssueAssignment.query.filter_by(assignment_status=AssignmentStatus.ASSIGNED).first()
    if not assignment:
        return # Skip if no assignment exists
        
    worker = User.query.get(assignment.assigned_to)
    headers = auth_headers(worker.email)
    
    data = {
        'status': 'REJECTED'
        # No reason provided
    }
    response = client.patch(f'/api/assignments/{assignment.id}/status', json=data, headers=headers)
    assert response.status_code == 400
    assert "reason is required" in response.json['error']

def test_transition_status_success(client, auth_headers):
    assignment = IssueAssignment.query.filter_by(assignment_status=AssignmentStatus.ASSIGNED).first()
    if not assignment:
        return
        
    worker = User.query.get(assignment.assigned_to)
    headers = auth_headers(worker.email)
    
    data = {
        'status': 'ACCEPTED'
    }
    response = client.patch(f'/api/assignments/{assignment.id}/status', json=data, headers=headers)
    assert response.status_code == 200
    assert response.json['assignment_status'] == 'accepted'
