import pytest
from app import create_app
from app.extensions import db
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.models.enums import UserRole

import tempfile
import os

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    # Use testing config
    app = create_app('development')
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "JWT_SECRET_KEY": "test-secret-key",
        "PROPAGATE_EXCEPTIONS": True,
        "RATELIMIT_ENABLED": False
    })
    # Mock redis_client and Celery tasks for tests
    from unittest.mock import patch
    patcher_redis = patch('app.middleware.auth_middleware.redis_client.get', return_value=None)
    patcher_redis.start()
    
    # Mock celery tasks so they don't try to connect to Redis
    patcher_process_event = patch('app.tasks.notification_tasks.process_issue_event.delay')
    patcher_process_event.start()
    
    patcher_sla = patch('app.tasks.sla_tasks.calculate_issue_sla.delay')
    patcher_sla.start()
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Create a dummy test user so tests can run
        officer = User(
            email='officer1@example.com',
            full_name='Test Officer',
            role=UserRole.MUNICIPAL_OFFICER,
            is_active=True,
            password_hash='dummy'
        )
        db.session.add(officer)
        
        # Add mock models for testing assignments
        from app.models.municipal import Ward, Department, EmployeeProfile
        from app.models.issue import Issue, IssueCategory
        from app.models.assignment import IssueAssignment
        from app.models.enums import AssignmentStatus
        
        ward = Ward(name="Test Ward", code="TW-1", city="Test City")
        department = Department(name="Test Dept", description="Test")
        db.session.add(ward)
        db.session.add(department)
        db.session.commit()
        
        worker = User(
            email='worker1@example.com',
            full_name='Test Worker',
            role=UserRole.FIELD_WORKER,
            is_active=True,
            password_hash='dummy'
        )
        inactive_worker = User(
            email='worker2@example.com',
            full_name='Inactive Worker',
            role=UserRole.FIELD_WORKER,
            is_active=False,
            password_hash='dummy'
        )
        db.session.add(worker)
        db.session.add(inactive_worker)
        db.session.commit()
        
        profile = EmployeeProfile(user_id=worker.id, department_id=department.id, ward_id=ward.id, employee_code="EMP-1", designation="Worker")
        db.session.add(profile)
        
        category = IssueCategory(name="Pothole")
        db.session.add(category)
        db.session.commit()
        
        issue = Issue(
            issue_number="ISS-1",
            title="Test Pothole",
            description="Big pothole",
            category_id=category.id,
            created_by=officer.id,
            ward_id=ward.id
        )
        db.session.add(issue)
        db.session.commit()
        
        assignment = IssueAssignment(
            issue_id=issue.id,
            assigned_to=worker.id,
            assigned_by=officer.id,
            department_id=department.id,
            ward_id=ward.id,
            assignment_status=AssignmentStatus.ASSIGNED
        )
        db.session.add(assignment)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except OSError:
        pass

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(app):
    def _auth_headers(email, role=UserRole.FIELD_WORKER):
        with app.app_context():
            user = User.query.filter_by(email=email).first()
            if not user:
                # auto create
                user = User(email=email, full_name='Auto', role=role, is_active=True, password_hash='dummy')
                db.session.add(user)
                db.session.commit()
            access_token = create_access_token(identity=user.id)
            return {'Authorization': f'Bearer {access_token}'}
    return _auth_headers
