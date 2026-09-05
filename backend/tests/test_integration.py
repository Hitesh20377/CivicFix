import pytest
import json
from app.models.enums import UserRole

def test_integration_issue_creation_and_retrieval(client, auth_headers):
    # Auth headers for a citizen
    headers = auth_headers("integration_citizen@example.com", UserRole.CITIZEN)
    
    # Create an issue
    issue_data = {
        "title": "Integration Test Pothole",
        "description": "This pothole is dangerous and deep.",
        "category_id": 1,
        "ward_id": 1,
        "latitude": 12.34,
        "longitude": 56.78
    }
    
    response = client.post(
        "/api/issues", 
        data=json.dumps(issue_data),
        headers=headers,
        content_type="application/json"
    )
    
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data["status"] == "success"
    assert "data" in response_data
    
    issue_id = response_data["data"]["id"]
    
    # Retrieve the issue
    get_response = client.get(
        f"/api/issues/{issue_id}",
        headers=headers
    )
    
    assert get_response.status_code == 200
    get_data = json.loads(get_response.data)
    assert get_data["data"]["title"] == "Integration Test Pothole"
