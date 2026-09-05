import { test, expect } from '@playwright/test';

test.describe('Admin Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'dummy');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/issues/);
  });

  test('Admin can access system overview', async ({ page }) => {
    // Admins see all issues
    await expect(page.locator('text=Test Pothole').first()).toBeVisible();
    
    // Test navigation or basic visibility of admin elements if they exist
    // Just verifying the user successfully logged in and dashboard loaded
    const pageTitle = page.locator('h1');
    await expect(pageTitle).toBeVisible();
  });
});
