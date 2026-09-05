import os
import pytest
from playwright.sync_api import Page, expect

# Set the base URL for the frontend
BASE_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

def test_citizen_workflow(page: Page):
    # 1. Register
    page.goto(f"{BASE_URL}/register")
    page.fill('input[placeholder*="First Name"]', "E2E")
    page.fill('input[placeholder*="Last Name"]', "Citizen")
    page.fill('input[type="email"]', "e2ecitizen@example.com")
    page.fill('input[type="password"]', "password123")
    page.click('button:has-text("Register")')

    # Wait for redirect to login or dashboard
    page.wait_for_url(f"**/login")
    
    # 2. Login
    page.fill('input[type="email"]', "e2ecitizen@example.com")
    page.fill('input[type="password"]', "password123")
    page.click('button:has-text("Login")')
    
    # After login, maybe redirected to /dashboard or /
    page.wait_for_url(f"**/")
    
    # 3. Create Issue
    page.click('text="Report Issue"')
    page.wait_for_url(f"**/create-issue*")
    
    page.fill('input[name="title"], input[placeholder*="Title"]', "E2E Broken Pothole")
    page.fill('textarea[name="description"], textarea[placeholder*="Description"]', "This is a massive pothole causing damage to cars.")
    
    # Select category and priority (assume select/dropdown exists)
    # page.select_option('select[name="categoryId"]', index=1)
    
    # Upload attachment (assuming input type file)
    with open("dummy.jpg", "wb") as f:
        f.write(b"dummy image content")
    page.set_input_files('input[type="file"]', "dummy.jpg")
    
    # Select location (click on the map)
    # Give map time to load
    page.wait_for_selector(".leaflet-container")
    page.click(".leaflet-container")
    
    page.click('button[type="submit"], button:has-text("Submit")')
    
    # 4. View Issue
    # Wait for dashboard
    page.wait_for_url(f"**/")
    
    # Click the new issue
    page.click('text="E2E Broken Pothole"')
    page.wait_for_url(f"**/issues/**")
    
    # 5. Track Status
    expect(page.locator("text=SUBMITTED")).to_be_visible()
    
    # 6. Add Comment
    page.fill('textarea[placeholder*="comment"], textarea[name="comment"]', "E2E test comment")
    page.click('button:has-text("Add Comment"), button:has-text("Submit")')
    
    expect(page.locator("text=E2E test comment")).to_be_visible()
