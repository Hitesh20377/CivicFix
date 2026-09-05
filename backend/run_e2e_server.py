import os
import sys

# Add backend to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Bypass Redis for local E2E testing
os.environ['REDIS_URL'] = 'memory://'

from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.enums import UserRole
from app.models.municipal import Ward, Department, EmployeeProfile
from app.models.issue import Issue, IssueCategory
from app.models.assignment import IssueAssignment
from app.models.enums import AssignmentStatus
from flask_jwt_extended import create_access_token

def setup_test_data(app):
    with app.app_context():
        db.drop_all()
        db.create_all()

        
        # 1. Admin
        admin = User(
            email='admin@example.com',
            full_name='System Admin',
            role=UserRole.ADMIN,
            is_active=True,
            password_hash=generate_password_hash('dummy')
        )
        db.session.add(admin)

        # 2. Citizen (Auth flow)
        citizen = User(
            email='integration_citizen@example.com',
            full_name='Integration Citizen',
            role=UserRole.CITIZEN,
            is_active=True,
            password_hash=generate_password_hash('dummy')
        )
        db.session.add(citizen)
        
        # Citizen (Issue flow)
        citizen2 = User(
            email='citizen@example.com',
            full_name='Issue Citizen',
            role=UserRole.CITIZEN,
            is_active=True,
            password_hash=generate_password_hash('dummy')
        )
        db.session.add(citizen2)

        # 3. Officer
        officer = User(
            email='officer1@example.com',
            full_name='Test Officer',
            role=UserRole.MUNICIPAL_OFFICER,
            is_active=True,
            password_hash=generate_password_hash('dummy')
        )
        db.session.add(officer)
        db.session.commit()

        # 4. Department & Ward
        ward = Ward(name="Test Ward", code="TW-1", city="Test City")
        department = Department(name="Test Dept", description="Test")
        db.session.add(ward)
        db.session.add(department)
        db.session.commit()
        
        # Officer Profile
        officer_profile = EmployeeProfile(user_id=officer.id, department_id=department.id, ward_id=ward.id, employee_code="OFF-1", designation="Officer")
        db.session.add(officer_profile)
        
        # 5. Field Worker
        worker = User(
            email='worker1@example.com',
            full_name='Test Worker',
            role=UserRole.FIELD_WORKER,
            is_active=True,
            password_hash=generate_password_hash('dummy')
        )
        db.session.add(worker)
        db.session.commit()

        
        profile = EmployeeProfile(user_id=worker.id, department_id=department.id, ward_id=ward.id, employee_code="EMP-1", designation="Worker")
        db.session.add(profile)
        
        # 6. Issue Category
        category = IssueCategory(name="Pothole")
        db.session.add(category)
        db.session.commit()
        
        # 7. Issue
        issue = Issue(
            issue_number="ISS-1",
            title="Test Pothole",
            description="Big pothole",
            category_id=category.id,
            created_by=citizen.id,
            ward_id=ward.id
        )
        db.session.add(issue)
        db.session.commit()
        
        # 8. Assignment
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
        
        print("E2E Test Data Seeded.")

if __name__ == '__main__':
    # Use testing config to use sqlite and bypass Redis/Celery needs
    app = create_app('development')
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///e2e_test.db",
        "JWT_SECRET_KEY": "test-secret-key",
        "PROPAGATE_EXCEPTIONS": True,
        "RATELIMIT_ENABLED": False,
        "WTF_CSRF_ENABLED": False
    })
    import celery.app.task
    celery.app.task.Task.delay = lambda self, *args, **kwargs: None
    
    # Create tables and seed data
    setup_test_data(app)

    # Run the app
    app.run(port=5000, debug=False, use_reloader=False)
