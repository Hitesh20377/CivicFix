import os
import sys
import pytest
from io import BytesIO

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.issue import Issue, IssueCategory
from app.models.enums import IssuePriority, IssueStatus, UserRole
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app('test')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def setup_data(app):
    citizen = User(
        email='test@example.com',
        full_name='Test Citizen',
        role=UserRole.CITIZEN,
        password_hash='dummyhash'
    )
    db.session.add(citizen)
    db.session.commit()
    
    category = IssueCategory(name='Test Category')
    db.session.add(category)
    db.session.commit()
    
    issue = Issue(
        issue_number='ISS-123456',
        title='Test Issue',
        description='Test Description',
        category_id=category.id,
        created_by=citizen.id,
        citizen_priority=IssuePriority.LOW,
        status=IssueStatus.SUBMITTED
    )
    db.session.add(issue)
    db.session.commit()
    
    token = create_access_token(identity=str(citizen.id))
    
    return {
        'citizen': citizen,
        'issue': issue,
        'token': token
    }

from unittest.mock import patch

def test_add_comment(client, setup_data):
    token = setup_data['token']
    issue_id = setup_data['issue'].id
    
    with patch('app.middleware.auth_middleware.redis_client.get') as mock_redis:
        mock_redis.return_value = None
        response = client.post(
            f'/api/issues/{issue_id}/comments',
            headers={'Authorization': f'Bearer {token}'},
            json={'comment': 'This is a test comment.'}
        )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['data']['comment'] == 'This is a test comment.'

def test_upload_attachment(client, setup_data):
    token = setup_data['token']
    issue_id = setup_data['issue'].id
    
    data = {
        'file': (BytesIO(b'dummy image content'), 'test.png')
    }
    
    with patch('app.middleware.auth_middleware.redis_client.get') as mock_redis:
        mock_redis.return_value = None
        response = client.post(
            f'/api/issues/{issue_id}/attachments',
            headers={'Authorization': f'Bearer {token}'},
            data=data,
            content_type='multipart/form-data'
        )
    
    assert response.status_code == 201
    res_data = response.get_json()
    assert res_data['status'] == 'success'
    assert res_data['data']['file_name'] == 'test.png'
    assert res_data['data']['file_type'] == 'png'
