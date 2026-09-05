import { test, expect } from '@playwright/test';

test.describe('Officer Assignment Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login as officer before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', 'officer1@example.com');
    await page.fill('input[type="password"]', 'dummy');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/issues/);
  });

  test('Officer can view issues and assign them', async ({ page }) => {
    // Check that issues are listed
    await expect(page.locator('text=Test Pothole').first()).toBeVisible();
    
    // Click on the first issue
    await page.locator('text=Test Pothole').first().click();
    
    // Expect to be on issue detail page
    await expect(page).toHaveURL(/\/issues\/\d+/);
    
    // Check that AssignmentManager component renders (it contains text like 'Assign' or 'Current Assignment')
    // We expect the officer to see the Assignment section since the issue is assigned.
    const assignLocator = page.locator('text=Assign').first();
    const currentAssignmentLocator = page.locator('text=Current Assignment').first();
    
    // Check if either is visible, Playwright wait
    await expect(assignLocator.or(currentAssignmentLocator)).toBeVisible();
  });
});
